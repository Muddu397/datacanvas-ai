const API_URL =
    "https://pvartqowob.execute-api.ap-south-1.amazonaws.com/latest";


const elements = {

    title: document.getElementById("story-title"),
    theme: document.getElementById("story-theme"),
    generated: document.getElementById("generated-text"),

    salesGrowth:
        document.getElementById("sales-growth"),

    topRegion:
        document.getElementById("top-region"),

    topRegionSales:
        document.getElementById("top-region-sales"),

    topProduct:
        document.getElementById("top-product"),

    topProductSales:
        document.getElementById("top-product-sales"),

    dataPoints:
        document.getElementById("data-points"),

    insight:
        document.getElementById("insight"),

    whyItMatters:
        document.getElementById("why-it-matters"),

    action:
        document.getElementById("action"),

    anomalyDate:
        document.getElementById("anomaly-date"),

    anomalyRegion:
        document.getElementById("anomaly-region"),

    anomalyProduct:
        document.getElementById("anomaly-product"),

    anomalyZScore:
        document.getElementById("anomaly-zscore"),

    chart:
        document.getElementById("sales-chart"),

    chartLabels:
        document.getElementById("chart-labels")
};


function formatNumber(value) {

    return new Intl.NumberFormat(
        "en-IN",
        {
            maximumFractionDigits: 0
        }
    ).format(value);

}


function formatCurrency(value) {

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0
        }
    ).format(value);

}


function formatDate(dateString) {

    const date = new Date(
        `${dateString}T00:00:00`
    );

    return date.toLocaleDateString(
        "en-IN",
        {
            day: "2-digit",
            month: "short"
        }
    );

}


function formatGeneratedTime(timestamp) {

    const date = new Date(timestamp);

    return date.toLocaleString(
        "en-IN",
        {
            dateStyle: "medium",
            timeStyle: "short"
        }
    );

}


/* ---------------------------------------------------------
   DRAW SVG SALES CHART
--------------------------------------------------------- */

function drawChart(chartData) {

    const svg = elements.chart;

    svg.innerHTML = "";

    if (!chartData || chartData.length === 0) {
        return;
    }

    const width = 900;
    const height = 330;

    const paddingX = 28;
    const paddingTop = 24;
    const paddingBottom = 30;

    const values =
        chartData.map(
            item => Number(item.sales)
        );

    const minValue =
        Math.min(...values);

    const maxValue =
        Math.max(...values);

    const range =
        maxValue - minValue || 1;


    const xStep =
        (width - paddingX * 2) /
        (chartData.length - 1);


    function getX(index) {

        return paddingX +
            index * xStep;

    }


    function getY(value) {

        return paddingTop +
            (
                (maxValue - value) /
                range
            ) *
            (
                height -
                paddingTop -
                paddingBottom
            );

    }


    /* Grid lines */

    for (let i = 0; i < 4; i++) {

        const y =
            paddingTop +
            i *
            (
                (height -
                    paddingTop -
                    paddingBottom)
                / 3
            );

        const line =
            document.createElementNS(
                "http://www.w3.org/2000/svg",
                "line"
            );

        line.setAttribute(
            "x1",
            paddingX
        );

        line.setAttribute(
            "x2",
            width - paddingX
        );

        line.setAttribute(
            "y1",
            y
        );

        line.setAttribute(
            "y2",
            y
        );

        line.setAttribute(
            "class",
            "chart-grid-line"
        );

        svg.appendChild(line);
    }


    /* Build line */

    let points = "";

    chartData.forEach(
        (item, index) => {

            points +=
                `${getX(index)},${getY(item.sales)} `;

        }
    );


    /* Area */

    const areaPoints =
        `${paddingX},${height - paddingBottom} ` +
        points +
        `${getX(chartData.length - 1)},${height - paddingBottom}`;

    const area =
        document.createElementNS(
            "http://www.w3.org/2000/svg",
            "polygon"
        );

    area.setAttribute(
        "points",
        areaPoints
    );

    area.setAttribute(
        "class",
        "chart-area"
    );

    svg.appendChild(area);


    /* Line */

    const polyline =
        document.createElementNS(
            "http://www.w3.org/2000/svg",
            "polyline"
        );

    polyline.setAttribute(
        "points",
        points
    );

    polyline.setAttribute(
        "class",
        "chart-line"
    );

    svg.appendChild(polyline);


    /* Points */

    chartData.forEach(
        (item, index) => {

            const circle =
                document.createElementNS(
                    "http://www.w3.org/2000/svg",
                    "circle"
                );

            circle.setAttribute(
                "cx",
                getX(index)
            );

            circle.setAttribute(
                "cy",
                getY(item.sales)
            );

            circle.setAttribute(
                "r",
                "4"
            );

            circle.setAttribute(
                "class",
                "chart-point"
            );

            svg.appendChild(circle);

        }
    );


    /* X labels */

    elements.chartLabels.innerHTML = "";

    chartData.forEach(
        (item, index) => {

            const label =
                document.createElement("span");

            label.textContent =
                formatDate(item.date);

            label.style.display =
                index % 2 === 0
                    ? "inline"
                    : "none";

            elements.chartLabels.appendChild(
                label
            );

        }
    );
}


/* ---------------------------------------------------------
   RENDER DATA
--------------------------------------------------------- */

function renderData(data) {

    const findings =
        data.findings || {};

    const growth =
        findings.growth || {};

    const topRegion =
        findings.top_region || {};

    const topProduct =
        findings.top_product || {};

    const anomaly =
        findings.strongest_anomaly;


    elements.title.textContent =
        data.title ||
        "Today's Data Discovery";


    elements.theme.textContent =
        data.theme ||
        "Autonomous Data Story";


    elements.generated.textContent =
        `Generated automatically • ${
            formatGeneratedTime(
                data.generated_at
            )
        }`;


    elements.salesGrowth.textContent =
        `${growth.sales_percent ?? 0}%`;


    elements.topRegion.textContent =
        topRegion.name ||
        "—";


    elements.topRegionSales.textContent =
        topRegion.sales != null
            ? formatCurrency(topRegion.sales)
            : "—";


    elements.topProduct.textContent =
        topProduct.name ||
        "—";


    elements.topProductSales.textContent =
        topProduct.sales != null
            ? formatCurrency(topProduct.sales)
            : "—";


    elements.dataPoints.textContent =
        formatNumber(
            findings.dataset_records || 0
        );


    elements.insight.textContent =
        data.insight ||
        "No insight available.";


    elements.whyItMatters.textContent =
        data.why_it_matters ||
        "No business context available.";


    elements.action.textContent =
        data.action ||
        "No recommendation available.";


    if (anomaly) {

        elements.anomalyDate.textContent =
            formatDate(anomaly.date);

        elements.anomalyRegion.textContent =
            anomaly.region;

        elements.anomalyProduct.textContent =
            anomaly.product;

        elements.anomalyZScore.textContent =
            anomaly.z_score;

    } else {

        elements.anomalyDate.textContent =
            "None detected";

        elements.anomalyRegion.textContent =
            "—";

        elements.anomalyProduct.textContent =
            "—";

        elements.anomalyZScore.textContent =
            "—";
    }


    drawChart(
        findings.chart_data || []
    );
}


/* ---------------------------------------------------------
   LOAD API
--------------------------------------------------------- */

async function loadData() {

    try {

        const response =
            await fetch(API_URL, {
                cache: "no-store"
            });


        if (!response.ok) {

            throw new Error(
                `API returned ${response.status}`
            );

        }


        const data =
            await response.json();


        renderData(data);


    } catch (error) {

        console.error(
            "DataCanvas API error:",
            error
        );

        elements.title.textContent =
            "Unable to load today's story";

        elements.theme.textContent =
            "The autonomous agent may be generating a new discovery.";

        elements.generated.textContent =
            "Waiting for the next successful agent run.";

    }
}


/* Initial load */

loadData();


/* Refresh every minute */

setInterval(
    loadData,
    60 * 1000
);