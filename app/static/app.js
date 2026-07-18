// Fetch the jobs from our FastAPI backend
fetch('/api/jobs')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(jobs => {
        // Strict Phase 2: Removed all hardcoded sample data fallbacks
        renderDashboard(jobs || []);
    })
    .catch(error => {
        console.error('Detailed Error:', error);
        document.getElementById('job-list').innerHTML = `
            <div style="background: #ffebee; color: #c62828; padding: 15px; border-radius: 6px; border: 1px solid #ef9a9a; margin-top: 20px;">
                <h4 style="margin-top:0;">⚠️ Error Loading Discovered Jobs</h4>
                <p style="margin-bottom:0; font-family: monospace; font-size: 13px;">${error.message}</p>
            </div>
        `;
    });

function renderDashboard(jobs) {
    const jobList = document.getElementById('job-list');
    jobList.innerHTML = ''; // Clear fallback states

    if (jobs.length === 0) {
        jobList.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #666; font-size: 14px;">
                <p><strong>No live jobs discovered yet.</strong></p>
                <p style="margin-top: 5px; font-size: 12px; color: #999;">The background scanner is executing. Refresh shortly once data populates.</p>
            </div>
        `;
        // Zero out stats cleanly
        document.getElementById('total-jobs').innerText = '0';
        document.getElementById('cv-matches').innerText = '0';
        document.getElementById('visa-count').innerText = '0';
        document.getElementById('permit-count').innerText = '0';
        document.getElementById('relo-count').innerText = '0';
        return;
    }

    jobs.forEach(job => {
        const card = document.createElement('div');
        card.className = 'job-card';
        card.innerHTML = `
            <h3>${job.title || 'Untitled Position'}</h3>
            <p><strong>${job.company || 'Discovered Employer'}</strong> — ${job.location || 'Global'}</p>
            <p>${job.description || 'No description available.'}</p>
            <div class="tags">
                <span>API Score: ${job.api_score !== undefined ? job.api_score : 'N/A'}</span>
                ${job.cv_match ? '<span>CV Match</span>' : ''}
                ${job.visa_sponsored ? '<span>Visa Sponsored</span>' : ''}
                ${job.work_permit ? '<span>Work Permit</span>' : ''}
                ${job.relocation ? '<span>Relocation</span>' : ''}
            </div>
        `;
        jobList.appendChild(card);
    });

    // Update Stats Counters dynamically using real records
    document.getElementById('total-jobs').innerText = jobs.length;
    document.getElementById('cv-matches').innerText = jobs.filter(j => j.cv_match).length;
    document.getElementById('visa-count').innerText = jobs.filter(j => j.visa_sponsored).length;
    document.getElementById('permit-count').innerText = jobs.filter(j => j.work_permit).length;
    document.getElementById('relo-count').innerText = jobs.filter(j => j.relocation).length;
}
