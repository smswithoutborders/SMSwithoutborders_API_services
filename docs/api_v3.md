# **API V3 Resource Documentation**

## **Base URL**

```
https://vault.smswithoutborders.com
```

## **Endpoints**

### **1. Get Signup Metrics**

Retrieve metrics for user signups within a specified date range, with options for filtering and pagination.

#### **Endpoint**

```
GET /v3/metrics/signup
```

#### **Query Parameters**

| Parameter      | Type   | Required | Description                                                                          |
| -------------- | ------ | -------- | ------------------------------------------------------------------------------------ |
| `start_date`   | string | Yes      | Start date in "YYYY-MM-DD" format.                                                   |
| `end_date`     | string | Yes      | End date in "YYYY-MM-DD" format.                                                     |
| `country_code` | string | No       | Country code for filtering signup users.                                             |
| `granularity`  | string | No       | Granularity for date grouping: "day" or "month". Defaults to "day".                  |
| `group_by`     | string | No       | Grouping option: "country", "date", or None. Defaults to None (returns total count). |
| `top`          | int    | No       | Limits the number of results returned (overrides `page` and `page_size`).            |
| `page`         | int    | No       | Page number for pagination. Defaults to `1`.                                         |
| `page_size`    | int    | No       | Number of records per page. Defaults to `50`. Maximum recommended value is `100`.    |

#### **Response**

**Status Code: 200 OK**

**Response Body:**

```json
{
  "total_signup_users": 120,
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_pages": 3,
    "total_records": 120
  },
  "data": [
    {
      "country_code": "CM",
      "signup_users": 30
    },
    {
      "timeframe": "2024-12-01",
      "signup_users": 20
    },
    ...
  ]
}
```

**Status Code: 400 Bad Request**

**Response Body (Examples):**

- Missing required parameters:
  ```json
  {
    "error": "Invalid input parameters. Provide 'start_date' and 'end_date'."
  }
  ```
- Invalid `page`, `page_size`, or conflicting parameters (e.g., `top` with pagination):
  ```json
  {
    "error": "'top' cannot be used with 'page' or 'page_size'."
  }
  ```
- Invalid `granularity` value:
  ```json
  {
    "error": "Invalid granularity. Use 'day' or 'month'."
  }
  ```
- Invalid `group_by` value:
  ```json
  {
    "error": "Invalid group_by value. Use 'country', 'date', or None."
  }
  ```

---

### **2. Get Retained User Metrics**

Retrieve metrics for retained (active) users within a specified date range, with options for filtering and pagination.

#### **Endpoint**

```
GET /v3/metrics/retained
```

#### **Query Parameters**

| Parameter      | Type   | Required | Description                                                                          |
| -------------- | ------ | -------- | ------------------------------------------------------------------------------------ |
| `start_date`   | string | Yes      | Start date in "YYYY-MM-DD" format.                                                   |
| `end_date`     | string | Yes      | End date in "YYYY-MM-DD" format.                                                     |
| `country_code` | string | No       | Country code for filtering retained users.                                           |
| `granularity`  | string | No       | Granularity for date grouping: "day" or "month". Defaults to "day".                  |
| `group_by`     | string | No       | Grouping option: "country", "date", or None. Defaults to None (returns total count). |
| `top`          | int    | No       | Limits the number of results returned (overrides `page` and `page_size`).            |
| `page`         | int    | No       | Page number for pagination. Defaults to `1`.                                         |
| `page_size`    | int    | No       | Number of records per page. Defaults to `50`. Maximum recommended value is `100`.    |

#### **Response**

**Status Code: 200 OK**

**Response Body:**

```json
{
  "total_retained_users": 75,
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_pages": 3,
    "total_records": 75
  },
  "data": [
    {
      "country_code": "CM",
      "retained_users": 25
    },
    {
      "timeframe": "2024-12-01",
      "retained_users": 15
    },
    ...
  ]
}
```

**Status Code: 400 Bad Request**

**Response Body (Examples):**

- Missing required parameters:
  ```json
  {
    "error": "Invalid input parameters. Provide 'start_date' and 'end_date'."
  }
  ```
- Invalid `page`, `page_size`, or conflicting parameters (e.g., `top` with pagination):
  ```json
  {
    "error": "'top' cannot be used with 'page' or 'page_size'."
  }
  ```
  - Invalid `granularity` value:
  ```json
  {
    "error": "Invalid granularity. Use 'day' or 'month'."
  }
  ```
- Invalid `group_by` value:
  ```json
  {
    "error": "Invalid group_by value. Use 'country', 'date', or None."
  }
  ```
