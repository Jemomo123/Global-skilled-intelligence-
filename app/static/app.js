// Fetch the jobs from our FastAPI backend
fetch('/api/jobs')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(jobs => {
        // Fallback sample jobs if the backend list is empty
        if (!jobs || jobs.length === 0) {
            console.log("No backend jobs found. Using fallback sample jobs for dashboard testing.");
            jobs = [
                {
                    "title": "Red Seal Plumber (Sample)",
                    "company": "Global Skilled Industries",
                    "location": "Toronto, ON",
                    "description": "Looking for an experienced Journeyman Plumber for commercial projects.",
                    "api_score": "100/100",
                    "cv_match": true,
                    "visa_sponsored": true,
                    "work_permit": true,
                    "relocation": true
                },
                {
                    "title": "Mechanical Fitter (Sample)",
                    "company": "Precision Engineering Ltd",
                    "location": "Vancouver, BC",
                    "description": "Seeking general fitter with mechanical engineering certificate for machinery maintenance.",
                    "api_score": "95/100",
                    "cv_match": true,
                    "visa_sponsored": false,
                    "work_permit": true,
                    "relocation": true
                }
            ];
        }

        renderDashboard(jobs);
    })
    .catch(error => {
        console.error('Detailed Error:', error);
        // Show the actual technical error on screen for easy debugging
        document.getElementById('job-list').innerHTML = `
            <div style="background: #ffebee; color: #c62828; padding: 15px; border-radius: 6px; border: 1px solid #ef9a9a; margin-top: 20px;">
                <h4 style="margin-top:0;">⚠️ Error Loading Discovered Jobs</h4>
                <p style="margin-bottom:0; font-family: monospace; font-size: 13px;">${error.message}</p>
            </div>
        `;
    });

function renderDashboard(jobs) {
    const jobList = document.getElementById('job-list');
    jobList.innerHTML = ''; // Clear loading message

    jobs.forEach(job => {
        const card = document.createElement('div');
        card.className = 'job-card';
        card.innerHTML = `
            <h3>${job.title}</h3>
            <p><strong>${job.company}</strong> — ${job.location}</p>
            <p>${job.description}</p>
            <div class="tags">
                <span>API Score: ${job.api_score}</span>
                ${job.cv_match ? '<span>CV Match</span>' : ''}
                ${job.visa_sponsored ? '<span>Visa Sponsored</span>' : ''}
                ${job.work_permit ? '<span>Work Permit</span>' : ''}
                ${job.relocation ? '<span>Relocation</span>' : ''}
            </div>
        `;
        jobList.appendChild(card);
    });

    // Update Stats Counters safely
    document.getElementById('total-jobs').innerText = jobs.length;
    document.getElementById('cv-matches').innerText = jobs.filter(j => j.cv_match).length;
    document.getElementById('visa-count').innerText = jobs.filter(j => j.visa_sponsored).length;
    document.getElementById('permit-count').innerText = jobs.filter(j => j.work_permit).length;
    document.getElementById('relo-count').innerText = jobs.filter(j => j.relocation).length;
}
