var ctx = document.getElementById('monthIncome').getContext('2d');

var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [{% for each in income_chart %}
                    "{{ each['period'] }}",
                    {% endfor %}
        ],
        datasets: [{
            label: '',
            data: [{% for each in income_chart %}
                    {{ each['value'] }},
                    {% endfor %}
                ]
        }]
        },
        options: {
            title: {
                display: false
            },

            legend:{
                display: false
            },

            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
    }
});