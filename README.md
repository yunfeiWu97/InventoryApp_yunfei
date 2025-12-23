# InventoryApp

An small inventory system using:

* **DynamoDB** – stores inventory items
* **AWS Lambda** – runs the backend code
* **API Gateway** – exposes the REST API
* **S3 static website** – simple front-end page (`index.html`)
* **GitHub Actions** – CI for linting and deployment

---

## Live demo
<img width="1331" height="869" alt="Weixin Image_2025-11-29_144700_305" src="https://github.com/user-attachments/assets/119d847f-45ca-407b-aa5d-1c82cc9bdb91" />

The live website can't be accessed because my course has ended and is no longer accessible o(╥﹏╥)o
---

## Features

Inventory items have:

* `item_id`
* `item_name`
* `item_description`
* `item_qty_on_hand`
* `item_price`
* `location_id`

The API supports:

* List all items
* Get one item by ID
* List all items for one location
* Add a new item
* Delete an item

---

## Project structure

```text
.
├─ index.html                 # Simple web page for S3 hosting
├─ lambda/
│  ├─ get_all_inventory_items/
│  │   └─ lambda_function.py
│  ├─ get_inventory_item/
│  │   └─ lambda_function.py
│  ├─ get_location_inventory_items/
│  │   └─ lambda_function.py
│  ├─ add_inventory_item/
│  │   └─ lambda_function.py
│  └─ delete_inventory_item/
│      └─ lambda_function.py
└─ .github/
   └─ workflows/
      ├─ superlinter.yml      # Runs Super-Linter on pull requests
      ├─ lambda_deploy.yml    # Deploys Lambda code on push to main
      └─ s3_website.yml       # Deploys index.html to S3 on push to main
```

---

## AWS setup (summary)

1. **DynamoDB**

   * Table name: `Inventory` (or the name used in the Lambda code).
   * Partition key: `item_id` (string).
   * Sample items are loaded for testing.

2. **Lambda functions**

   Five functions are created in AWS console with these names:

   * `get_all_inventory_items`
   * `get_inventory_item`
   * `get_location_inventory_items`
   * `add_inventory_item`
   * `delete_inventory_item`

   Each function uses the matching `lambda/<function_name>/lambda_function.py`.

3. **API Gateway**

   A REST API is created with stage `prod` and base URL like:

   ```text
   https://<rest-api-id>.execute-api.us-east-1.amazonaws.com/prod
   ```

   Endpoints:

   * `GET  /item`
   * `GET  /item/{id}`
   * `GET  /location/{id}`
   * `POST /item`
   * `DELETE /item/{id}`

   Each method is integrated with the correct Lambda function.

4. **S3 static website**

   * Bucket name: something like `inventoryapp-<name>-2025`.
   * Static website hosting is enabled.
   * `index.html` is uploaded and can be opened via the S3 website URL.

---

## GitHub Actions

Secrets (repository → **Settings → Secrets and variables → Actions**):

* `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`
* `AWS_SESSION_TOKEN`

Need to update each time re-open

Workflows:

1. **Super-Linter (`superlinter.yml`)**

   * Trigger: `pull_request` (opened or reopened).
   * Checks code style for Python, HTML, YAML, etc.
   * Used for peer review on the `dev` branch.

2. **Deploy Python functions to Lambda (`lambda_deploy.yml`)**

   * Trigger: `push` to `main` **only when** Lambda Python files under `lambda/` change.
   * Zips each `lambda_function.py` and runs `aws lambda update-function-code` for the matching function name.

3. **Deploy website to S3 (`s3_website.yml`)**

   * Trigger: `push` to `main` **only when** `index.html` changes.
   * Runs `aws s3 sync` to copy `index.html` to the S3 bucket.

---

## Git workflow

* Day-to-day work is done on the **`dev`** branch.
* When a feature is ready, create a **pull request** from `dev` → `main`.
* Super-Linter runs automatically on the PR.
* After peer review, the PR is merged into `main`.
* Merge to `main` triggers:

  * Lambda deploy workflow (if Lambda files changed)
  * S3 deploy workflow (if `index.html` changed)

---

## API testing (Postman / Restfox)

Example base URL (replace with real one):

```text
https://<rest-api-id>.execute-api.us-east-1.amazonaws.com/prod
```

1. **List all items**

   * Method: `GET`
   * URL: `{{baseUrl}}/item`

2. **Get one item by ID**

   * Method: `GET`
   * URL: `{{baseUrl}}/item/01TESTITEM1`

3. **List items by location**

   * Method: `GET`
   * URL: `{{baseUrl}}/location/1`

4. **Add new item**

   * Method: `POST`
   * URL: `{{baseUrl}}/item`
   * Body (raw JSON):

     ```json
     {
       "item_name": "Green Hat",
       "item_description": "Size M, cotton",
       "item_qty_on_hand": 3,
       "item_price": 15.5,
       "location_id": 1
     }
     ```

5. **Delete item**

   * Method: `DELETE`
   * URL: `{{baseUrl}}/item/01TESTITEM1`

---

