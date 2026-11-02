
const API_URL = "http://127.0.0.1:8000";

// Login function
async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const message = document.getElementById("message");

    try {
        const response = await fetch(
            `${API_URL}/api/accounts/login/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            message.textContent = "Login failed. Check your credentials.";
            return;
        }

        // Save the authentication token
        localStorage.setItem("token", data.token);

        message.textContent = "Login successful! Welcome " + data.username;

        console.log("Logged in user:", data);

    } catch (error) {
        message.textContent = "Could not connect to Django.";
        console.error(error);
    }
}

async function loadJobs() {
    const jobsContainer = document.getElementById("jobs");

    jobsContainer.textContent = "Loading jobs...";

    try {
        const response = await fetch(
            `${API_URL}/api/jobs/`
        );

        if (!response.ok) {
            throw new Error("Could not load jobs.");
        }

        const jobs = await response.json();

        jobsContainer.innerHTML = "";

        if (jobs.length === 0) {
            jobsContainer.textContent = "No jobs available.";
            return;
        }

        jobs.forEach(job => {
            const jobCard = document.createElement("div");

            const title = document.createElement("h3");
            title.textContent = job.title;

            const company = document.createElement("p");
            company.textContent = "Company: " + job.company_name;

            const location = document.createElement("p");
            location.textContent = "Location: " + job.location;

            const employment = document.createElement("p");
            employment.textContent = "Type: " + job.employment_type;

            jobCard.append(title, company, location, employment);
            jobsContainer.appendChild(jobCard);
        });

    } catch (error) {
        jobsContainer.textContent = "Error loading jobs.";
        console.error(error);
    }
}

async function loadCV() {
    const cvContainer = document.getElementById("cv");

    const token = localStorage.getItem("token");

    if (!token) {
        cvContainer.textContent = "Please login first.";
        return;
    }

    cvContainer.textContent = "Loading CV profile...";

    try {
        const response = await fetch(
            `${API_URL}/api/cv/profile/`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Token ${token}`
                }
            }
        );

        if (!response.ok) {
            throw new Error("Could not load CV profile.");
        }

        const profile = await response.json();

        cvContainer.innerHTML = "";

        for (const [key, value] of Object.entries(profile)) {
            const paragraph = document.createElement("p");
            paragraph.textContent = `${key}: ${value ?? ""}`;
            cvContainer.appendChild(paragraph);
        }

    } catch (error) {
        cvContainer.textContent = "Error loading CV profile.";
        console.error(error);
    }
}

async function loadEducation() {
    const educationContainer = document.getElementById("education");
    const token = localStorage.getItem("token");

    if (!token) {
        educationContainer.textContent = "Please login first.";
        return;
    }

    educationContainer.textContent = "Loading education...";

    try {
        const response = await fetch(
            `${API_URL}/api/cv/education/`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Token ${token}`
                }
            }
        );

        if (!response.ok) {
            throw new Error("Could not load education.");
        }

        const records = await response.json();

        educationContainer.innerHTML = "";

        if (records.length === 0) {
            educationContainer.textContent = "No education records found.";
            return;
        }

        records.forEach(record => {
            const card = document.createElement("div");

            const degree = document.createElement("h3");
            degree.textContent = record.degree;

            const institution = document.createElement("p");
            institution.textContent = "Institution: " + record.institution;

            const field = document.createElement("p");
            field.textContent = "Field: " + record.field_of_study;

            const years = document.createElement("p");
            years.textContent = `Years: ${record.start_year} - ${record.end_year ?? "Present"}`;

            const grade = document.createElement("p");
            grade.textContent = "Grade: " + record.grade;

            card.append(degree, institution, field, years, grade);
            educationContainer.appendChild(card);
        });

    } catch (error) {
        educationContainer.textContent = "Error loading education.";
        console.error(error);
    }
}
