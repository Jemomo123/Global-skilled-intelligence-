document.addEventListener("DOMContentLoaded", () => {
    const jobListEl = document.getElementById("job-list");
    const countryFilterEl = document.getElementById("country-filter");
    
    let allJobs = [];

    async function fetchJobs() {
        try {
            const res = await fetch("/api/jobs/discover");
            allJobs = await res.json();
            populateCountryFilter(allJobs);
            updateDashboard(allJobs);
        } catch (err) {
            console.error("Error fetching jobs:", err);
            jobListEl.innerHTML = "<p>Error loading discovered jobs.</p>";
        }
    }

    function populateCountryFilter(jobs) {
        const countries = new Set();
        jobs.forEach(job => {
            if (job.country) {
                countries.add(job.country);
            }
        });
        
        countries.forEach(country => {
            const opt = document.createElement("option");
            opt.value = country;
            opt.textContent = country;
            countryFilterEl.appendChild(opt);
        });
    }

    function updateDashboard(jobs) {
        // UI directly reads pre-computed intelligence flags from Python
        document.getElementById("total-jobs").textContent = jobs.length;
        document.getElementById("visa-count").textContent = jobs.filter(j => j.visa_sponsored).length;
        document.getElementById("relo-count").textContent = jobs.filter(j => j.relocation_offered).length;
        document.getElementById("permit-count").textContent = jobs.filter(j => j.work_permit_support).length;
        document.getElementById("cv-matches").textContent = jobs.filter(j => j.cv_match).length;

        renderJobList(jobs);
    }

    function renderJobList(jobs) {
        jobListEl.innerHTML = "";
        if (jobs.length === 0) {
            jobListEl.innerHTML = "<p>No jobs found.</p>";
            return;
        }

        jobs.forEach(job => {
            const card = document.createElement("div");
            card.className = "job-card";
            
            let badges = `<span class="badge">${job.source_type.toUpperCase()}</span>`;
            badges += `<span class="badge score">Score: ${job.job_score}/100</span>`;
            
            if (job.cv_match) {
                badges += `<span class="badge match">CV Match</span>`;
            }
            if (job.visa_sponsored) {
                badges += `<span class="badge visa">Visa Sponsored</span>`;
            }
            if (job.work_permit_support) {
                badges += `<span class="badge permit">Work Permit</span>`;
            }
            if (job.relocation_offered) {
                badges += `<span class="badge relo">Relocation</span>`;
            }

            card.innerHTML = `
                <div class="job-title">${job.title}</div>
                <div class="job-meta">${job.company} — <strong>${job.location}</strong></div>
                <div style="margin-bottom: 8px; font-size: 14px;">${job.description}</div>
                <div>${badges}</div>
            `;
            jobListEl.appendChild(card);
        });
    }

    countryFilterEl.addEventListener("change", (e) => {
        const selectedCountry = e.target.value;
        if (!selectedCountry) {
            renderJobList(allJobs);
        } else {
            const filtered = allJobs.filter(job => job.country === selectedCountry);
            renderJobList(filtered);
        }
    });

    fetchJobs();
});
          
