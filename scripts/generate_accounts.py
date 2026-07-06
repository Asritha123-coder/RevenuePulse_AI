from faker import Faker
import pandas as pd
import random
import os
from datetime import datetime

fake = Faker()

NUM_ACCOUNTS = 3000

industries = [
    "Healthcare",
    "Finance",
    "Retail",
    "Education",
    "Manufacturing",
    "IT Services",
    "Telecommunications",
    "Energy",
    "Logistics",
    "E-Commerce"
]

company_sizes = [
    "Startup",
    "Small Business",
    "Mid Market",
    "Enterprise"
]

countries = {
    "India": {
        "states": ["Telangana", "Karnataka", "Tamil Nadu", "Maharashtra", "Andhra Pradesh", "Delhi", "Kerala"],
        "cities": ["Hyderabad", "Bengaluru", "Chennai", "Mumbai", "Vijayawada", "Delhi", "Kochi"]
    },
    "USA": {
        "states": ["California", "Texas", "New York", "Florida"],
        "cities": ["San Francisco", "Austin", "New York", "Miami"]
    },
    "UK": {
        "states": ["England", "Scotland"],
        "cities": ["London", "Edinburgh"]
    },
    "Germany": {
        "states": ["Bavaria", "Berlin"],
        "cities": ["Munich", "Berlin"]
    },
    "Canada": {
        "states": ["Ontario", "British Columbia"],
        "cities": ["Toronto", "Vancouver"]
    },
    "Singapore": {
        "states": ["Singapore"],
        "cities": ["Singapore"]
    }
}

status = ["Active", "Inactive"]

sales_managers = [
    "Rahul Sharma",
    "Priya Singh",
    "John Miller",
    "Sneha Reddy",
    "Arjun Verma",
    "David Wilson",
    "Sarah Johnson",
    "Meera Nair"
]

records = []

for i in range(1, NUM_ACCOUNTS + 1):

    account_id = f"ACC{i:06d}"

    company_name = fake.company()

    industry = random.choice(industries)

    size = random.choices(
        company_sizes,
        weights=[20, 35, 30, 15],
        k=1
    )[0]

    if size == "Startup":
        employees = random.randint(10, 50)
        revenue = random.randint(5_00_000, 50_00_000)

    elif size == "Small Business":
        employees = random.randint(50, 250)
        revenue = random.randint(50_00_000, 5_00_00_000)

    elif size == "Mid Market":
        employees = random.randint(250, 1000)
        revenue = random.randint(5_00_00_000, 50_00_00_000)

    else:
        employees = random.randint(1000, 10000)
        revenue = random.randint(50_00_00_000, 1000_00_00_000)

    country = random.choice(list(countries.keys()))

    state = random.choice(countries[country]["states"])

    city = random.choice(countries[country]["cities"])

    account_status = random.choices(
        status,
        weights=[90,10],
        k=1
    )[0]

    owner = random.choice(sales_managers)

    customer_since = fake.date_between(
        start_date="-5y",
        end_date="-1y"
    )

    last_activity = fake.date_between(
        start_date=customer_since,
        end_date="today"
    )

    records.append({
        "account_id": account_id,
        "company_name": company_name,
        "industry": industry,
        "company_size": size,
        "employee_count": employees,
        "annual_revenue": revenue,
        "country": country,
        "state": state,
        "city": city,
        "account_status": account_status,
        "account_owner": owner,
        "customer_since": customer_since,
        "last_activity": last_activity
    })

df = pd.DataFrame(records)

# ----------------------------
# Inject Data Quality Issues
# ----------------------------

# Duplicate 5%
duplicates = df.sample(frac=0.05, random_state=42)
df = pd.concat([df, duplicates], ignore_index=True)

# Missing state (3%)
state_null = df.sample(frac=0.03).index
df.loc[state_null, "state"] = None

# Missing revenue (2%)
rev_null = df.sample(frac=0.02).index
df.loc[rev_null, "annual_revenue"] = None

# Wrong country names (4%)
country_wrong = df.sample(frac=0.04).index

wrong_names = [
    "USA",
    "U.S.A.",
    "US",
    "United States"
]

for idx in country_wrong:
    df.at[idx, "country"] = random.choice(wrong_names)

# Negative revenue (1%)
negative = df.sample(frac=0.01).index

for idx in negative:
    if pd.notnull(df.at[idx, "annual_revenue"]):
        df.at[idx, "annual_revenue"] *= -1

# Mixed date formats (5%)
mixed_dates = df.sample(frac=0.05).index

for idx in mixed_dates:
    dt = pd.to_datetime(df.at[idx, "customer_since"])

    fmt = random.choice([
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%b %d %Y"
    ])

    df.at[idx, "customer_since"] = dt.strftime(fmt)

# ----------------------------
# Save CSV
# ----------------------------

output_dir = "datasets/raw"

os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "accounts.csv")

df.to_csv(output_path, index=False)

print("="*50)
print("Accounts Dataset Generated Successfully")
print(f"Total Records : {len(df)}")
print(f"Saved At      : {output_path}")
print("="*50)