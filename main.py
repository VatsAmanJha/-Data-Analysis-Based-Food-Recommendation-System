from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

# Load your dataset
df1 = pd.read_csv(r"archive\FOOD-DATA-GROUP1.csv")
df2 = pd.read_csv(r"archive\FOOD-DATA-GROUP2.csv")
df3 = pd.read_csv(r"archive\FOOD-DATA-GROUP3.csv")
df4 = pd.read_csv(r"archive\FOOD-DATA-GROUP4.csv")
df = pd.concat([df1, df2, df3, df4], ignore_index=True)
df.drop_duplicates(inplace=True)

# Initialize FastAPI app
app = FastAPI()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Define columns available for selection
available_columns = [
    "food",
    "Carbohydrates",
    "Protein",
    "Fat",
    "Caloric Value",
    "Nutrition Density",
    "Vitamin A",
    "Vitamin B1",
    "Vitamin B6",
    "Vitamin B12",
    "Vitamin C",
    "Vitamin D",
    "Calcium",
    "Iron",
    "Magnesium",
    "Zinc",
]
df = df[available_columns]


# Define FastAPI endpoint for home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "columns": available_columns[1:]}
    )


# Define FastAPI endpoint for recommendation
@app.post("/recommend/", response_class=HTMLResponse)
async def recommend_foods(
    request: Request,
    high_columns: str = Form(...),
    low_columns: str = Form(...),
    exclude_columns: str = Form(...),
):
    # Function to filter data based on selected column and option
    def filter_data(df, columns, option):
        filtered_df = pd.DataFrame()
        if columns:
            columns_list = columns.split(",")
            for column in columns_list:
                if option == "high":
                    filtered_df = pd.concat(
                        [
                            filtered_df,
                            df.sort_values(by=column, ascending=False).head(),
                        ]
                    )
                elif option == "low":
                    filtered_df = pd.concat(
                        [filtered_df, df.sort_values(by=column, ascending=True).head()]
                    )
            # Exclude option handled by dropping column later
        return filtered_df.drop_duplicates()

    # Filter based on user's selection for high columns
    filtered_high = filter_data(df, high_columns, "high")

    # Filter based on user's selection for low columns
    recommend_foods = filter_data(filtered_high, low_columns, "low")

    # Drop excluded columns
    if exclude_columns:
        exclude_columns_list = exclude_columns.split(",")
        recommend_foods = recommend_foods.drop(
            columns=exclude_columns_list, errors="ignore"
        )

    # Convert dataframe to dictionary for template rendering
    foods_dict = recommend_foods.head().to_dict(orient="records")

    return templates.TemplateResponse(
        "recommendation.html", {"request": request, "foods": foods_dict}
    )
