const renderChart = (id_el, data, labels, chart_type, title) => {
    var ctx = document.getElementById(id_el).getContext("2d");
    var myChart = new Chart(ctx, {
      type: chart_type,
      data: {
        labels: labels,
        datasets: [
          {
            label: "Last 6 months expenses",
            data: data,
            backgroundColor: [
              "rgba(255, 99, 132, 0.2)",
              "rgba(54, 162, 235, 0.2)",
              "rgba(255, 206, 86, 0.2)",
              "rgba(75, 192, 192, 0.2)",
              "rgba(153, 102, 255, 0.2)",
              "rgba(255, 159, 64, 0.2)",
            ],
            borderColor: [
              "rgba(255, 99, 132, 1)",
              "rgba(54, 162, 235, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(75, 192, 192, 1)",
              "rgba(153, 102, 255, 1)",
              "rgba(255, 159, 64, 1)",
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        title: {
          display: true,
          text: title,
        },
      },
    });
  };
  
  const getChartData = () => {
    console.log("fetching");
    fetch("")
      .then((res) => res.json())
      .then((results) => {
        console.log("results", results);
        const category_data = results.data_line;
        console.log(category_data)
        // const [labels, data] = [
        // ,
        // [12, 19, 3, 5, 2, 3],
        // ];
  
        renderChart("Chart_evol",data, labels, 'line', "Evolution par type d'actifs");
        
        renderChart("Chart_proportion",data, labels, 'doughnut', "Répartition par type d'actifs");
      });
  };
  
  document.onload = getChartData();
  