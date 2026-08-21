import boto3
import csv
import json
import math
import statistics
from datetime import datetime, timezone
from io import StringIO

# ============================================================
# DataCanvas AI - Autonomous Data Storyteller
# ============================================================

REGION = "ap-south-1"
BUCKET = "datacanvas-ai-mudasser-2026"

DATA_KEY = "data/datacanvas_sample_data.csv"
LATEST_OUTPUT_KEY = "outputs/latest.json"

MODEL_ID = "apac.amazon.nova-lite-v1:0"

s3 = boto3.client("s3", region_name=REGION)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)


# ------------------------------------------------------------
# Read CSV from S3
# ------------------------------------------------------------

def load_dataset():
    print("Loading dataset from S3...")

    response = s3.get_object(
        Bucket=BUCKET,
        Key=DATA_KEY
    )

    content = response["Body"].read().decode("utf-8")

    reader = csv.DictReader(StringIO(content))

    rows = []

    for row in reader:
        rows.append({
            "date": row["date"],
            "region": row["region"],
            "product": row["product"],
            "sales": float(row["sales"]),
            "customers": int(row["customers"]),
            "orders": int(row["orders"])
        })

    print(f"Loaded {len(rows)} records.")

    return rows


# ------------------------------------------------------------
# Basic helper functions
# ------------------------------------------------------------

def percentage_change(old, new):
    if old == 0:
        return 0

    return ((new - old) / old) * 100


def safe_round(value, digits=2):
    return round(float(value), digits)


# ------------------------------------------------------------
# Data Science analysis
# ------------------------------------------------------------

def analyze_data(rows):

    print("Running Data Science analysis...")

    total_sales = sum(r["sales"] for r in rows)
    total_customers = sum(r["customers"] for r in rows)
    total_orders = sum(r["orders"] for r in rows)

    dates = sorted(set(r["date"] for r in rows))

    # --------------------------------------------------------
    # Daily aggregation
    # --------------------------------------------------------

    daily = {}

    for r in rows:

        if r["date"] not in daily:
            daily[r["date"]] = {
                "sales": 0,
                "customers": 0,
                "orders": 0
            }

        daily[r["date"]]["sales"] += r["sales"]
        daily[r["date"]]["customers"] += r["customers"]
        daily[r["date"]]["orders"] += r["orders"]

    daily_sales = [
        {
            "date": d,
            "sales": safe_round(daily[d]["sales"]),
            "customers": daily[d]["customers"],
            "orders": daily[d]["orders"]
        }
        for d in dates
    ]

    # --------------------------------------------------------
    # Growth analysis
    # --------------------------------------------------------

    midpoint = len(dates) // 2

    first_period = dates[:midpoint]
    second_period = dates[midpoint:]

    first_sales = sum(daily[d]["sales"] for d in first_period)
    second_sales = sum(daily[d]["sales"] for d in second_period)

    first_customers = sum(
        daily[d]["customers"] for d in first_period
    )

    second_customers = sum(
        daily[d]["customers"] for d in second_period
    )

    first_orders = sum(
        daily[d]["orders"] for d in first_period
    )

    second_orders = sum(
        daily[d]["orders"] for d in second_period
    )

    sales_growth = percentage_change(
        first_sales,
        second_sales
    )

    customer_growth = percentage_change(
        first_customers,
        second_customers
    )

    order_growth = percentage_change(
        first_orders,
        second_orders
    )

    # --------------------------------------------------------
    # Region analysis
    # --------------------------------------------------------

    region_stats = {}

    for r in rows:

        region = r["region"]

        if region not in region_stats:
            region_stats[region] = {
                "sales": 0,
                "customers": 0,
                "orders": 0
            }

        region_stats[region]["sales"] += r["sales"]
        region_stats[region]["customers"] += r["customers"]
        region_stats[region]["orders"] += r["orders"]

    top_region = max(
        region_stats,
        key=lambda x: region_stats[x]["sales"]
    )

    # --------------------------------------------------------
    # Product analysis
    # --------------------------------------------------------

    product_stats = {}

    for r in rows:

        product = r["product"]

        if product not in product_stats:
            product_stats[product] = {
                "sales": 0,
                "customers": 0,
                "orders": 0
            }

        product_stats[product]["sales"] += r["sales"]
        product_stats[product]["customers"] += r["customers"]
        product_stats[product]["orders"] += r["orders"]

    top_product = max(
        product_stats,
        key=lambda x: product_stats[x]["sales"]
    )

    # --------------------------------------------------------
    # Product growth
    # --------------------------------------------------------

    product_growth = {}

    for product in product_stats:

        first = sum(
            r["sales"]
            for r in rows[:]
            if r["product"] == product
            and r["date"] in first_period
        )

        second = sum(
            r["sales"]
            for r in rows[:]
            if r["product"] == product
            and r["date"] in second_period
        )

        product_growth[product] = percentage_change(
            first,
            second
        )

    fastest_growing_product = max(
        product_growth,
        key=product_growth.get
    )

    # --------------------------------------------------------
    # Anomaly detection
    # --------------------------------------------------------
    # Detect unusual region/product combinations by comparing
    # sales values within each combination.

    groups = {}

    for r in rows:

        key = (r["region"], r["product"])

        if key not in groups:
            groups[key] = []

        groups[key].append(r)

    anomalies = []

    for key, group in groups.items():

        values = [r["sales"] for r in group]

        if len(values) < 5:
            continue

        mean = statistics.mean(values)

        stdev = statistics.stdev(values)

        if stdev == 0:
            continue

        for r in group:

            z_score = (r["sales"] - mean) / stdev

            if abs(z_score) >= 3:

                anomalies.append({
                    "date": r["date"],
                    "region": r["region"],
                    "product": r["product"],
                    "sales": safe_round(r["sales"]),
                    "z_score": safe_round(z_score, 2)
                })

    anomalies.sort(
        key=lambda x: abs(x["z_score"]),
        reverse=True
    )

    strongest_anomaly = (
        anomalies[0]
        if anomalies
        else None
    )

    # --------------------------------------------------------
    # Chart data
    # --------------------------------------------------------

    chart_data = daily_sales[-14:]

    findings = {
        "dataset_records": len(rows),
        "date_range": {
            "start": dates[0],
            "end": dates[-1]
        },

        "total_sales": safe_round(total_sales),
        "total_customers": total_customers,
        "total_orders": total_orders,

        "growth": {
            "sales_percent": safe_round(sales_growth),
            "customers_percent": safe_round(customer_growth),
            "orders_percent": safe_round(order_growth)
        },

        "top_region": {
            "name": top_region,
            "sales": safe_round(
                region_stats[top_region]["sales"]
            )
        },

        "top_product": {
            "name": top_product,
            "sales": safe_round(
                product_stats[top_product]["sales"]
            )
        },

        "fastest_growing_product": {
            "name": fastest_growing_product,
            "growth_percent": safe_round(
                product_growth[fastest_growing_product]
            )
        },

        "strongest_anomaly": strongest_anomaly,

        "chart_data": chart_data
    }

    print("Analysis complete.")

    print(
        json.dumps(
            findings,
            indent=2
        )
    )

    return findings


# ------------------------------------------------------------
# Read previous DataCanvas story
# ------------------------------------------------------------

def load_previous_story():

    try:

        response = s3.get_object(
            Bucket=BUCKET,
            Key=LATEST_OUTPUT_KEY
        )

        previous = json.loads(
            response["Body"].read().decode("utf-8")
        )

        return {
            "title": previous.get("title", ""),
            "theme": previous.get("theme", ""),
            "insight": previous.get("insight", "")
        }

    except Exception:

        print("No previous story found. This is the first run.")

        return None


# ------------------------------------------------------------
# Generate creative data story using Amazon Bedrock
# ------------------------------------------------------------

def generate_story(findings, previous_story):

    print("Calling Amazon Bedrock...")

    previous_context = "No previous story exists."

    if previous_story:

        previous_context = f"""
Previous story title:
{previous_story.get("title")}

Previous theme:
{previous_story.get("theme")}

Previous insight:
{previous_story.get("insight")}
"""

    prompt = f"""
You are DataCanvas AI, an autonomous data storytelling agent.

Your job is to transform verified Data Science findings into a compelling,
original, concise, and business-relevant data story.

The Python analysis below contains VERIFIED statistics.
You MUST use only the supplied findings.
Never invent, estimate, modify, or hallucinate numerical values.

VERIFIED DATA FINDINGS:

{json.dumps(findings, indent=2)}

PREVIOUS STORY CONTEXT:

{previous_context}

============================================================
STORYTELLING INSTRUCTIONS
============================================================

Each autonomous run should tell a FRESH story about the same dataset.

Select ONE primary storytelling angle from the following possibilities:

1. PRODUCT GROWTH
   Focus on the fastest-growing or strongest-performing product.

2. REGIONAL PERFORMANCE
   Focus on the strongest-performing region and its business significance.

3. BUSINESS MOMENTUM
   Focus on overall sales, customer, and order growth.

4. ANOMALY DISCOVERY
   Focus on the strongest detected anomaly and why it deserves investigation.

5. STRATEGIC OPPORTUNITY
   Identify the most actionable business opportunity supported by the findings.

6. SALES TREND
   Focus on the recent sales trajectory and notable changes in performance.

Choose the angle that is most interesting and useful for the current run.

IMPORTANT:
- Do NOT use the same primary angle as the previous story.
- Do NOT simply rewrite the previous story using different words.
- If the previous story focused on a product, prefer a region, anomaly,
  business momentum, trend, or strategic opportunity next.
- If the previous story focused on a region, choose another angle.
- Rotate storytelling perspectives across autonomous runs.
- The underlying verified numbers may remain the same because the source
  dataset has not changed. The interpretation and business story should
  change.
- Every numerical claim must come directly from VERIFIED DATA FINDINGS.
- Do not invent causes for an anomaly unless the data supports them.
- Do not claim that a trend is increasing, decreasing, or consistent unless
  the supplied data supports that statement.
- Keep the story professional and suitable for a business dashboard.

============================================================
OUTPUT REQUIREMENTS
============================================================

Create:

1. A creative but professional title.
2. A short theme describing the selected storytelling angle.
3. A concise 2-3 sentence insight.
4. A clear explanation of why the finding matters to the business.
5. One practical and actionable recommendation.

The insight should clearly reflect the selected storytelling angle.

The recommendation should directly follow from the insight.

If an anomaly is relevant to the selected story, mention it.
If it is not relevant, do not force it into the story.

Return ONLY valid JSON.
Do not include markdown.
Do not include ```json.
Do not include any explanation outside the JSON.

Use EXACTLY this structure:

{{
  "title": "Creative business-focused title",
  "theme": "Short storytelling theme",
  "insight": "2-3 sentence explanation of the key finding",
  "why_it_matters": "Why this finding matters to the business",
  "action": "One practical recommendation"
}}
"""

    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "inferenceConfig": {
            "maxTokens": 700,
            "temperature": 0.7,
            "topP": 0.9
        }
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(request_body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(
        response["body"].read()
    )

    generated_text = (
        response_body["output"]
        ["message"]
        ["content"][0]
        ["text"]
    )

    print("Bedrock response:")
    print(generated_text)

    # --------------------------------------------------------
    # Parse JSON response
    # --------------------------------------------------------

    try:

        story = json.loads(generated_text)

    except json.JSONDecodeError:

        print(
            "Model did not return clean JSON. "
            "Using fallback parser."
        )

        cleaned = (
            generated_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            story = json.loads(cleaned)

        except Exception:

            story = {
                "title": "Today's Data Discovery",
                "theme": "Hidden Patterns",
                "insight": generated_text,
                "why_it_matters": (
                    "The analysis revealed a meaningful "
                    "pattern in the dataset."
                ),
                "action": (
                    "Investigate the highlighted pattern "
                    "for further opportunities."
                )
            }

    return story


# ------------------------------------------------------------
# Save result to S3
# ------------------------------------------------------------

def save_output(findings, story):

    now = datetime.now(timezone.utc)

    output = {
        "project": "DataCanvas AI",
        "generated_at": now.isoformat(),

        "title": story.get(
            "title",
            "Today's Data Discovery"
        ),

        "theme": story.get(
            "theme",
            "Data Discovery"
        ),

        "insight": story.get(
            "insight",
            ""
        ),

        "why_it_matters": story.get(
            "why_it_matters",
            ""
        ),

        "action": story.get(
            "action",
            ""
        ),

        "findings": findings,

        "agent": {
            "model": MODEL_ID,
            "trigger": "AWS Lambda",
            "source": "Amazon S3"
        }
    }

    payload = json.dumps(
        output,
        indent=2
    )

    # Save latest result
    s3.put_object(
        Bucket=BUCKET,
        Key=LATEST_OUTPUT_KEY,
        Body=payload.encode("utf-8"),
        ContentType="application/json"
    )

    # Save historical copy
    date_key = now.strftime("%Y-%m-%d")

    historical_key = (
        f"outputs/{date_key}.json"
    )

    s3.put_object(
        Bucket=BUCKET,
        Key=historical_key,
        Body=payload.encode("utf-8"),
        ContentType="application/json"
    )

    print(
        f"Saved latest output to: "
        f"{LATEST_OUTPUT_KEY}"
    )

    print(
        f"Saved historical output to: "
        f"{historical_key}"
    )

    return output


# ------------------------------------------------------------
# Lambda entry point
# ------------------------------------------------------------

def lambda_handler(event, context):

    print("=" * 60)
    print("DATACANVAS AI AGENT STARTED")
    print("=" * 60)

    try:

        # 1. Load data
        rows = load_dataset()

        # 2. Perform Data Science analysis
        findings = analyze_data(rows)

        # 3. Retrieve previous agent memory
        previous_story = load_previous_story()

        # 4. Generate creative narrative
        story = generate_story(
            findings,
            previous_story
        )

        # 5. Save output
        output = save_output(
            findings,
            story
        )

        print("=" * 60)
        print("DATACANVAS AI AGENT COMPLETED")
        print("=" * 60)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "DataCanvas generation successful",
                "title": output["title"],
                "generated_at": output["generated_at"]
            })
        }

    except Exception as e:

        print("=" * 60)
        print("DATACANVAS AI AGENT FAILED")
        print("=" * 60)

        print(str(e))

        raise