from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json
import os
import uvicorn

app = FastAPI(title="Industrial Asset Monitor")

# Point FastAPI to the templates sub-folder
templates = Jinja2Templates(directory="templates")

DATA_FILE = "factory_data.json"
DEFAULT_STOCK = {
    "Chamber Valves": {"quantity": 12, "min_required": 5},
    "Robotic Sensors": {"quantity": 3, "min_required": 5},
    "Safety Goggles": {"quantity": 45, "min_required": 10},
    "Vacuum Seals": {"quantity": 2, "min_required": 4}
}


def load_data():
    """Loads inventory tracking details from a JSON file."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(DEFAULT_STOCK, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    """Saves updated asset data to the JSON storage."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, error: str | None = None):
    """Renders the main html user panel."""
    inventory = load_data()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "inventory": inventory, "error": error},
    )


@app.post("/use/{item_name}")
async def use_item(item_name: str):
    """Decreases an inventory item count by 1."""
    inventory = load_data()
    if item_name in inventory and inventory[item_name]["quantity"] > 0:
        inventory[item_name]["quantity"] -= 1
        save_data(inventory)
    return RedirectResponse(url="/", status_code=303)


@app.post("/restock/{item_name}")
async def restock_item(item_name: str):
    """Increases an inventory item count by 5."""
    inventory = load_data()
    if item_name in inventory:
        inventory[item_name]["quantity"] += 5
        save_data(inventory)
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{item_name}")
async def delete_item(item_name: str):
    """Removes an item from inventory entirely."""
    inventory = load_data()
    if item_name in inventory:
        del inventory[item_name]
        save_data(inventory)
    return RedirectResponse(url="/", status_code=303)


@app.post("/add")
async def add_item(
    item_name: str = Form(...),
    quantity: int = Form(...),
    min_required: int = Form(...),
):
    """Adds a brand new inventory item directly from the UI form."""
    item_name = item_name.strip()
    inventory = load_data()

    # Basic validation so the UI can't create broken or duplicate entries
    if not item_name:
        return RedirectResponse(url="/?error=Item+name+cannot+be+empty", status_code=303)
    if item_name in inventory:
        return RedirectResponse(url="/?error=That+item+already+exists", status_code=303)
    if quantity < 0 or min_required < 0:
        return RedirectResponse(url="/?error=Values+cannot+be+negative", status_code=303)

    inventory[item_name] = {"quantity": quantity, "min_required": min_required}
    save_data(inventory)
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
