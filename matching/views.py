
import re
from datetime import date

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import JobSeekerProfile
from accounts.permissions import IsJobSeeker
from cv_builder.models import (
    CVProfile,
    Skill,
    Education,
    WorkExperience,
    Certification,
)
from jobs.models import Job
from jobs.serializers import JobSerializer


class JobRecommendationsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsJobSeeker]

    def calculate_experience(self, user):
        """
        Use the seeker's manually entered experience when available.
        Otherwise, calculate experience from CV work history.
        Overlapping employment periods are counted only once.
        """
        seeker_profile = JobSeekerProfile.objects.filter(
            user=user
        ).first()

        if (
            seeker_profile
            and seeker_profile.total_experience_years > 0
        ):
            return float(seeker_profile.total_experience_years)

        experiences = WorkExperience.objects.filter(
            cv_profile__user=user
        )

        intervals = []

        for experience in experiences:
            start = experience.start_date
            end = (
                date.today()
                if experience.is_current or not experience.end_date
                else experience.end_date
            )

            if end >= start:
                intervals.append((start, end))

        if not intervals:
            return 0.0

        intervals.sort(key=lambda interval: interval[0])

        merged_intervals = []
        current_start, current_end = intervals[0]

        for start, end in intervals[1:]:
            if start <= current_end:
                current_end = max(current_end, end)
            else:
                merged_intervals.append(
                    (current_start, current_end)
                )
                current_start, current_end = start, end

        merged_intervals.append((current_start, current_end))

        total_days = sum(
            (end - start).days
            for start, end in merged_intervals
        )

        return round(total_days / 365.25, 2)

    def calculate_tfidf_similarity(
        self,
        candidate_text,
        job_text
    ):
        """
        Calculate lexical similarity using TF-IDF and cosine similarity.
        Returns a percentage between 0 and 100.
        """
        if not candidate_text.strip() or not job_text.strip():
            return 0.0

        try:
            vectorizer = TfidfVectorizer()

            tfidf_matrix = vectorizer.fit_transform([
                candidate_text,
                job_text
            ])

            similarity = cosine_similarity(
                tfidf_matrix[0:1],
                tfidf_matrix[1:2]
            )[0][0]

            return round(float(similarity) * 100, 2)

        except ValueError:
            return 0.0

    def get_candidate_text(self, user):
        """
        Combine the seeker's CV information into one text document.
        """
        parts = []

        cv_profile = CVProfile.objects.filter(
            user=user
        ).first()

        if cv_profile:
            parts.extend([
                cv_profile.professional_title,
                cv_profile.career_objective,
            ])

        seeker_profile = JobSeekerProfile.objects.filter(
            user=user
        ).first()

        if seeker_profile:
            parts.extend([
                seeker_profile.headline,
                seeker_profile.career_objective,
            ])

        skills = Skill.objects.filter(
            cv_profile__user=user
        )

        parts.extend(skill.name for skill in skills)

        education_records = Education.objects.filter(
            cv_profile__user=user
        )

        for education in education_records:
            parts.extend([
                education.degree,
                education.field_of_study,
                education.description,
            ])

        work_records = WorkExperience.objects.filter(
            cv_profile__user=user
        )

        for work in work_records:
            parts.extend([
                work.job_title,
                work.company,
                work.description,
            ])

        certifications = Certification.objects.filter(
            cv_profile__user=user
        )

        for certification in certifications:
            parts.extend([
                certification.name,
                certification.issuing_organization,
            ])

        return " ".join(
            str(part).strip()
            for part in parts
            if part and str(part).strip()
        )

    def get(self, request):
        # Get the candidate's CV skills.
        seeker_skills = Skill.objects.filter(
            cv_profile__user=request.user
        )

        skill_map = {
            skill.name.strip().casefold(): skill.name.strip()
            for skill in seeker_skills
            if skill.name.strip()
        }

        # Prepare candidate information.
        candidate_text = self.get_candidate_text(request.user)
        candidate_experience = self.calculate_experience(
            request.user
        )

        recommendations = []

        # Only recommend active jobs.
        jobs = Job.objects.filter(
            is_active=True
        ).order_by("-created_at")

        for job in jobs:

            # 1. SKILL MATCHING — 50%
            required_skills = [
                skill.strip()
                for skill in re.split(
                    r"[,;\n|]+",
                    job.required_skills
                )
                if skill.strip()
            ]

            required_map = {
                skill.casefold(): skill
                for skill in required_skills
            }

            matched_skills = [
                skill_map[skill]
                for skill in required_map
                if skill in skill_map
            ]

            missing_skills = [
                required_map[skill]
                for skill in required_map
                if skill not in skill_map
            ]

            if required_map:
                skill_percentage = (
                    len(matched_skills)
                    / len(required_map)
                ) * 100
            else:
                # No required skills means no skill requirement is unmet.
                skill_percentage = 100.0

            skill_percentage = round(skill_percentage, 2)

            # 2. EXPERIENCE MATCHING — 30%
            required_experience = job.min_experience_years

            if required_experience == 0:
                experience_percentage = 100.0
            else:
                experience_percentage = min(
                    candidate_experience
                    / required_experience * 100,
                    100.0
                )

            experience_percentage = round(
                experience_percentage, 2
            )

            # 3. TF-IDF + COSINE SIMILARITY — 20%
            job_text = " ".join([
                job.title,
                job.description,
                job.required_skills,
                job.category,
                job.location,
                job.employment_type,
            ])

            tfidf_percentage = self.calculate_tfidf_similarity(
                candidate_text,
                job_text
            )

            # Calculate weighted points.
            skill_points = round(
                skill_percentage * 0.50, 2
            )

            experience_points = round(
                experience_percentage * 0.30, 2
            )

            tfidf_points = round(
                tfidf_percentage * 0.20, 2
            )

            # FINAL MATCH SCORE — 100%
            final_score = round(
                skill_points
                + experience_points
                + tfidf_points,
                2
            )

            # Prepare the job response.
            job_data = JobSerializer(job).data

            job_data.update({
                "match_percentage": final_score,

                "skill_match_percentage": skill_percentage,
                "skill_match_score": skill_points,

                "experience_match_percentage": experience_percentage,
                "experience_match_score": experience_points,

                "tfidf_similarity_percentage": tfidf_percentage,
                "tfidf_similarity_score": tfidf_points,

                "candidate_experience_years": candidate_experience,
                "required_experience_years": required_experience,

                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
            })

            recommendations.append(job_data)

        # Rank jobs from highest to lowest final score.
        recommendations.sort(
            key=lambda item: item["match_percentage"],
            reverse=True
        )

        return Response({
            "count": len(recommendations),
            "results": recommendations
        })
    