document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.app-alert');
    alerts.forEach((alert, index) => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 300);
        }, 2600 + index * 500);
    });

    document.querySelectorAll('tbody tr').forEach(row => {
        row.addEventListener('click', (event) => {
            if (event.target.closest('button, a, form, input, select, textarea, label')) {
                return;
            }
            row.classList.toggle('table-active');
        });
    });

    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const btn = form.querySelector('button[type="submit"]');
            if (btn && !btn.dataset.originalText) {
                btn.dataset.originalText = btn.innerHTML;
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Working...';
            }
        });
    });

    document.querySelectorAll('[data-copy]').forEach(button => {
        button.addEventListener('click', async () => {
            const text = button.getAttribute('data-copy') || '';
            try {
                await navigator.clipboard.writeText(text);
                const original = button.innerText;
                button.innerText = 'Copied';
                setTimeout(() => button.innerText = original, 1200);
            } catch {
                alert('Copy failed.');
            }
        });
    });
});

function confirmDelete() {
    return confirm('Are you sure you want to delete this record?');
}

function confirmDeleteAll() {
    return confirm('This will delete ALL of your expenses. Continue?');
}
