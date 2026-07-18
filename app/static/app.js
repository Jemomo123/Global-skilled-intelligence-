document.addEventListener('DOMContentLoaded', () => {
    const jobList = document.getElementById('job-list');
    const countryFilter = document.getElementById('country-filter');

    // Initialize tracking metrics containers dynamically if they exist
    const totalDiscoveredEl = document.getElementById('total-discovered');
    const cvMatchesEl = document.getElementById('cv-matches');
    const visaSponsoredEl = document.getElementById('visa-sponsored');
    const workPermitEl = document.getElementById('work-permit');
    const relocationEl = document.getElementById('relocation');

    function updateMetrics(jobs) {
        if (totalDiscoveredEl) totalDiscoveredEl.textContent = jobs.length;
        if (cvMatchesEl) cvMatchesEl.textContent = jobs.filter(j => j.cv_match).length;
        if (visaSponsoredEl) visaSponsoredEl.textContent = jobs.filter(j => j.visa_sponsored).length;
        if (workPermitEl) workPermitEl.textContent = jobs.filter(j => j.work_permit).length;
        if (relocationEl) relocationEl.textContent = jobs.filter(j => j.relocation).length;
    }

    function renderJobs(jobs) {
        jobList.innerHTML = '';
        if (jobs.length === 0) {
            jobList.innerHTML = '<p style="text-align:center; padding: 20px; color: #666;">No matching vacancies discovered for your trade profile.</p>';
            return;
        }

        jobs.forEach(job => {
            const card = document.createElement('div');
            card.className = 'job-card';
            card.style.border = '1px solid #e0e0e0';
            card.style.borderRadius = '8px';
            card.style.padding = '16px';
            card.style.marginBottom = '16px';
            card.style.background = '#ffffff';
            
            const displayLocation = (job.city && job.country) ? `${job.city}, ${job.country}` : (job.location || job.country || 'Skilled Region');
            const postDate = job.date_discovered ? new Date(job.date_discovered).toLocaleDateString(undefined, {month: 'short', day: 'numeric', year: 'numeric'}) : 'Recent';

            card.innerHTML = `
                <div class="job-card-header">
                    <h3 style="margin: 0 0 4px 0; color: #111; font-size: 1.25em;">${job.title || 'Untitled Position'}</h3>
                    <p style="margin: 0 0 8px 0; color: #333;"><strong>${job.company || 'Discovered Employer'}</strong> — ${displayLocation}</p>
                </div>
                
                <div class="job-metadata-details" style="font-size: 0.85em; color: #666; margin: 8px 0;">
                    <span>💼 ${job.employment_type || 'Full-time'}</span> | 
                    <span>💰 ${job.salary || 'N/A'}</span> | 
                    <span>📅 ${postDate}</span>
                </div>

                <p class="job-description" style="color: #444; font-size: 0.95em; line-height: 1.4; margin: 12px 0;">${job.description || 'No description available.'}</p>
                
                <div class="tags" style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px;">
                    <span class="badge score-badge" style="background: #f0f4f8; color: #1a56db; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: 600;">API Score: ${job.api_score !== undefined ? job.api_score : 'N/A'}</span>
                    ${job.cv_match ? `<span class="badge match-tag" style="background:#e8f5e9; color:#2e7d32; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold;">CV Match: ${job.cv_match_pct || 0}%</span>` : ''}
                    ${job.visa_sponsored ? '<span class="badge" style="background: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">Visa Sponsored</span>' : ''}
                    ${job.work_permit ? '<span class="badge" style="background: #d1ecf1; color: #0c5460; padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">Work Permit</span>' : ''}
                    ${job.relocation ? '<span class="badge" style="background: #e2e3e5; color: #383d41; padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">Relocation</span>' : ''}
                </div>

                <div class="job-actions" style="margin-top: 12px;">
                    <a href="${job.job_url}" target="_blank" rel="noopener noreferrer" class="apply-btn" 
                       style="display: inline-block; background: #0076d6; color: #fff; padding: 8px 16px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 0.9em; text-align: center; border: none; width: 100%; box-sizing: border-box;">
                       Apply Now ↗
                    </a>
                </div>
            `;
            jobList.appendChild(card);
        });
    }

    async function fetchJobs() {
        try {
            const country = countryFilter ? countryFilter.value : 'all countries';
            let url = '/api/jobs';
            if (country && country.toLowerCase() !== 'all countries') {
                url += `?country=${encodeURIComponent(country)}`;
            }
            const res = await fetch(url);
            if (!res.ok) throw new Error('API pipeline connection fault');
            const data = await res.json();
            renderJobs(data);
            updateMetrics(data);
        } catch (err) {
            console.error('Error fetching jobs:', err);
        }
    }

    if (countryFilter) {
        countryFilter.addEventListener('change', fetchJobs);
    }

    // Initial run on boot
    fetchJobs();
});
