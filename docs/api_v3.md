# API V3 Resource Documentation

## **Base URL**

```
https://vault.smswithoutborders.com
```

## **Endpoints**

### **1. Get Signup Metrics**

Retrieve metrics for user signups within a specified date range.

#### **Endpoint**

```
GET /v3/signup-metrics
```

#### **Query Parameters**

| Parameter   | Type   | Required | Description                                                                       |
| ----------- | ------ | -------- | --------------------------------------------------------------------------------- |
| `start`     | string | Yes      | Start date in "YYYY-MM-DD" format.                                                |
| `end`       | string | Yes      | End date in "YYYY-MM-DD" format.                                                  |
| `page`      | int    | No       | Page number for pagination. Defaults to `1`.                                      |
| `page_size` | int    | No       | Number of records per page. Defaults to `10`. Maximum recommended value is `100`. |

#### **Response**

**Status Code: 200 OK**

**Response Body:**

```json
{
  "total_signup_count": 120,
  "total_country_count": 4,
  "data": {
    "2024-01-01": {
      "CM": { "signup_count": 30 },
      "NG": { "signup_count": 20 }
    },
    "2024-01-02": {
      "CA": { "signup_count": 50 },
      "AU": { "signup_count": 20 }
    }
  }
}
```

**Status Code: 400 Bad Request**

**Response Body (Examples):**

- Missing required parameters:
  ```json
  {
    "error": "Invalid input parameters. Provide 'start' and 'end' dates."
  }
  ```
- Invalid `page` or `page_size`:
  ```json
  {
    "error": "'page' and 'page_size' must be integers."
  }
  ```

---

### **2. Get Retained User Metrics**

Retrieve metrics for retained (active) users within a specified date range.

#### **Endpoint**

```
GET /v3/retained-user-metrics
```

#### **Query Parameters**

| Parameter   | Type   | Required | Description                                                                       |
| ----------- | ------ | -------- | --------------------------------------------------------------------------------- |
| `start`     | string | Yes      | Start date in "YYYY-MM-DD" format.                                                |
| `end`       | string | Yes      | End date in "YYYY-MM-DD" format.                                                  |
| `page`      | int    | No       | Page number for pagination. Defaults to `1`.                                      |
| `page_size` | int    | No       | Number of records per page. Defaults to `10`. Maximum recommended value is `100`. |

#### **Response**

**Status Code: 200 OK**

**Response Body:**

```json
{
  "total_retained_user_count": 75,
  "total_country_count": 4,
  "data": {
    "2024-01-01": {
      "CM": { "retained_user_count": 25 },
      "NG": { "retained_user_count": 15 }
    },
    "2024-01-02": {
      "CA": { "retained_user_count": 20 },
      "AU": { "retained_user_count": 15 }
    }
  }
}
```

**Status Code: 400 Bad Request**

**Response Body (Examples):**

- Missing required parameters:
  ```json
  {
    "error": "Invalid input parameters. Provide 'start' and 'end' dates."
  }
  ```
- Invalid `page` or `page_size`:
  ```json
  {
    "error": "'page' and 'page_size' must be integers."
  }
  ```
