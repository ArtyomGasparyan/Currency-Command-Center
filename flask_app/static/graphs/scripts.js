$(document).ready(function() {
    function fetchData(startDate, endDate) {
        $.getJSON(`/data?start_date=${startDate}&end_date=${endDate}`, function(data) {
            if (data.length > 0) {
                renderChart(data);
            } else {
                alert("No data available for the selected date range.");
            }
        }).fail(function() {
            alert("Failed to fetch data. Please check the server and network.");
        });
    }

    function renderChart(data) {
        const ctx = document.getElementById('exchangeRatesChart').getContext('2d');
        const labels = data.map(row => row.Date);
        const eurData = data.map(row => row.EUR);
        const gbpData = data.map(row => row.GBP);
        const rubData = data.map(row => row.RUB);
        const usdData = data.map(row => row.USD);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    { label: 'EUR', data: eurData, borderColor: 'blue', fill: false },
                    { label: 'GBP', data: gbpData, borderColor: 'green', fill: false },
                    { label: 'RUB', data: rubData, borderColor: 'red', fill: false },
                    { label: 'USD', data: usdData, borderColor: 'orange', fill: false }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: { display: true, title: { display: true, text: 'Date' } },
                    y: { display: true, title: { display: true, text: 'Exchange Rate' } }
                }
            }
        });
    }

    // Set default date range for the last 30 days
    const today = new Date().toISOString().split('T')[0];
    const lastMonth = new Date();
    lastMonth.setDate(lastMonth.getDate() - 30);
    const lastMonthDate = lastMonth.toISOString().split('T')[0];

    $('#start_date').val(lastMonthDate);
    $('#end_date').val(today);

    // Fetch data on page load with default date range
    fetchData(lastMonthDate, today);

    // Fetch data when filter button is clicked
    $('#filter').on('click', function() {
        const startDate = $('#start_date').val();
        const endDate = $('#end_date').val();
        fetchData(startDate, endDate);
    });
});
