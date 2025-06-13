document.addEventListener('DOMContentLoaded', () => {
    // ===== データ取得用ボタンの処理 =====
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            fetch(fetchUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Success!');
                    location.reload();  // 成功後に再読み込みして最新グラフを表示
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => alert('Fetch error: ' + error));
        });
    }

    // ===== グラフ描画の処理 =====
    const chartData = document.getElementById('chart-data');
    if (chartData) {
        const labels = JSON.parse(chartData.dataset.labels);
        const dataValues = JSON.parse(chartData.dataset.values);

        const canvas = document.getElementById('myPieChart');
        const message = document.getElementById('no-data-message');

        if (dataValues.length === 0 || dataValues.reduce((a, b) => a + b, 0) === 0) {
            canvas.style.display = 'none';
            message.style.display = 'block';
        } else {
            canvas.style.display = 'block';
            const ctx = canvas.getContext('2d');
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: dataValues,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 206, 86, 0.6)'
                        ]
                    }]
                },
                options: {
                    responsive: false
                }
            });
        }
    }
});

// ===== CSRF トークン取得関数 =====
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
