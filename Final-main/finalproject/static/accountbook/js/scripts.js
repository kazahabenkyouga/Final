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



document.addEventListener('DOMContentLoaded', () => {
  const chartData = document.getElementById('chart-data');
  if (!chartData) return;

  const canvas = document.getElementById('myPieChart');
  const message = document.getElementById('no-data-message');
  const categoryBtn = document.getElementById('category-btn');
  const tagBtn = document.getElementById('tag-btn');

  let myPieChart = null;

  function parseData(raw) {
    if (!raw) return [];
    const replaced = raw.replace(/\\u0027/g, "'");
    const doubleQuoted = replaced.replace(/'/g, '"');
    try {
      return JSON.parse(doubleQuoted);
    } catch (e) {
      console.error("JSON parse error:", e, "input:", doubleQuoted);
      return [];
    }
  }

  const categoryLabels = parseData(chartData.dataset.labels);
  const categoryValues = JSON.parse(chartData.dataset.values);
  const tagLabels = parseData(chartData.dataset.tagLabels);
  const tagValues = JSON.parse(chartData.dataset.tagValues);

  function drawChart(labels, values) {
    if (myPieChart) myPieChart.destroy();

    if (values.length === 0 || values.reduce((a, b) => a + b, 0) === 0) {
      canvas.style.display = 'none';
      message.style.display = 'block';
      return;
    } else {
      canvas.style.display = 'block';
      message.style.display = 'none';
    }

    const ctx = canvas.getContext('2d');
    myPieChart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)',
            'rgba(255, 159, 64, 0.6)',
            'rgba(201, 203, 207, 0.6)',
            'rgba(255, 99, 255, 0.6)',
            'rgba(100, 181, 246, 0.6)'
          ]
        }]
      },
      options: { responsive: false }
    });
  }

  // 初期表示
  drawChart(categoryLabels, categoryValues);
  categoryBtn.classList.add('active');

  // ボタン切り替え
  categoryBtn.addEventListener('click', () => {
    if (!categoryBtn.classList.contains('active')) {
      categoryBtn.classList.add('active');
      tagBtn.classList.remove('active');
      drawChart(categoryLabels, categoryValues);
    }
  });

  tagBtn.addEventListener('click', () => {
    if (!tagBtn.classList.contains('active')) {
      tagBtn.classList.add('active');
      categoryBtn.classList.remove('active');
      drawChart(tagLabels, tagValues);
    }
  });

    // ===== データ取得用ボタンの処理 =====
    const refreshBtn = document.getElementById('refresh-btn');
    console.log(refreshBtn);
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
                    if (data.updated) {
                       alert('新しいデータを取得しました。');
                    } else {
                        alert('最新の情報です。更新はありません。');
                    }
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => alert('Fetch error: ' + error));
        });
    }
});


fetch('/accountbook/check_latest_uncategorized/')
  .then(response => response.json())
  .then(data => {
    if (data.has_uncategorized) {
      showCategoryModal(data);  // モーダルを開く関数に渡す
    }
  });


function showCategoryModal(data) {
  const modalMessage = document.getElementById('modal-message');
  modalMessage.textContent = `日時: ${data.usage_datetime}\n金額: ${data.amount}`;

  const categoryModalElement = document.getElementById('categoryModal');
  const categoryModalInstance = new bootstrap.Modal(categoryModalElement);
  categoryModalInstance.show();

  const saveBtn = document.getElementById('save-category-btn');
  const categorySelect = document.getElementById('category-select');

  // 二重バインド防止
  saveBtn.onclick = null;

  saveBtn.onclick = () => {
    const selectedCategory = categorySelect.value;
    if (!selectedCategory) {
      alert('カテゴリーを選択してください');
      return;
    }

    fetch('/accountbook/update_categories/',  {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
body: JSON.stringify({ updates: [{ id: data.id, category: selectedCategory }] })
    })
    .then(res => res.json())
    .then(result => {
      if (result.success) {
        alert('カテゴリーを更新しました');
        categoryModalInstance.hide();
        location.reload();
      } else {
        alert('更新失敗: ' + result.error);
      }
    })
    .catch(e => {
      alert('通信エラーが発生しました');
      console.error(e);
    });
  };
}
