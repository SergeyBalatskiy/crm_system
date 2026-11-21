# Django Views Documentation

[Русский](VIEWS.md) | [English](VIEWS.en.md)

This document describes the main Django views in the CRM System project, including their HTTP methods and responsibilities.

## Contents

- [auth_registration](#1-auth_registration)
- [finance](#2-finance)
- [orders](#3-orders)
- [profile_user](#4-profile_user)
- [services](#5-services)
- [storage](#6-storage)

---

## 1. auth_registration

This application handles user registration and authentication.

| View | HTTP Methods | Description |
|---|---|---|
| `RegisterView` | GET, POST | Displays the registration form and handles new user creation using `CustomUserCreationForm`. |
| `CustomLoginView` | GET, POST | Displays the login form and handles user authentication using `LoginForm`. |
| `ShowForm` | GET | Displays the login and registration forms. |

## 2. finance

This application handles financial operations and cash balance management.

| View | HTTP Methods | Description |
|---|---|---|
| `BuyFinanceCustomView` | POST | Creates a financial operation in the "Other > Income" category using `SellCustomForm()`. |
| `SellFinanceCustomView` | POST | Creates a financial operation in the "Other > Expense" category using `BuyCustomForm()`. |
| `MainCashAndHistoryView` | GET | Displays the service center balance and filtered financial transaction history. |
| `InsertCashInBalance` | GET, POST | Displays `InsertCashForm()` and handles the creation of a financial operation in the "Product sale" category. |
| `ShowOthersCustomView` | GET | Displays `BuyCustomForm()` and `SellCustomForm()`. |
| `CountryAutocomplete` | GET | Searches and filters `StorageInfo` objects for autocomplete functionality. |

## 3. orders

This application handles orders, customer information, services associated with orders, payments, and document generation.

| View | HTTP Methods | Description |
|---|---|---|
| `ChangeStatusOrder` | GET, POST | Displays available statuses and saves the selected order status. |
| `ShowClientOrder` | GET, POST | Displays information about an existing order using `FormsForOrder` and the `json_forms` JSON field. |
| `DeleteServicesInOrder` | POST | Deletes an existing work item associated with an order. |
| `CountDsc` | POST | Calculates a discount based on the total order amount. |
| `FindClientInformation` | GET | Searches for existing customers in the `Client` model. |
| `ShowFormForOrder` | GET, POST | Retrieves data from the database and displays the current order form fields. |
| `GetTotalCount` | GET | Returns the total amount of items associated with an order. |
| `ShowAndPayView` | POST | Receives the payment amount and payment type, creates a `FinanceHistoryInfo` record, updates the balance, and generates a document. |
| `PrintSelectedDocument` | GET, POST | Populates an HTML document template with actual data and sends the generated document to the user. |
| `OrdersDetailsAutocomplete` | GET | Searches `StorageInfo` objects for autocomplete functionality when working with orders. |
| `ServicesSelectAutocomplete` | GET | Searches for services in `ServicesInfo` to provide autocomplete functionality. |
| `ServiceWorkCreate` | GET, POST | Displays `WorkCreatingForm()` and handles the creation of work items associated with an order. |
| `FindWorkersInformation` | GET | Retrieves employee information from `WorkersInfo`. |
| `ShowAndFilterOrders` | GET | Displays the order list and provides filtering and search functionality. |

## 4. profile_user

This application handles user profiles, service center information, employee management, and document management.

| View | HTTP Methods | Description |
|---|---|---|
| `ShowAdoptionView` | GET, POST | Displays `DocumentInfoForm()` and handles the creation of an acceptance document. |
| `BackupDocumentView` | GET | Restores the selected document to its default state. |
| `ShowCancellView` | GET, POST | Uses `DocumentInfoForm()` to create a refusal or cancellation document. |
| `ShowCategoriesView` | GET, POST | Displays and handles the creation of `StatusCategory` objects. |
| `ChangePersonalInformationView` | GET, POST | Displays the current user's personal information and handles updates. |
| `ShowCompleteView` | GET, POST | Uses `DocumentInfoForm()` to create a completed-work document. |
| `CreateNewFormInCategory` | GET, POST | Processes JSON form data, saves the form, and displays the form creation window. |
| `DeleteCustomForm` | POST | Deletes a custom form from `FormsForOrder`. |
| `FormsForOrdersEdit` | GET, POST | Displays active forms and handles adding, deleting, and changing their order in JSON data. |
| `ShowGarantyView` | GET, POST | Uses `DocumentInfoForm()` to create a warranty document. |
| `EditIndividualCenterForm` | GET, POST | Displays an automatic response form and saves its data in JSON format. |
| `UserProfileView` | GET | Displays the user profile, filters financial operations, and provides a dataset for JavaScript. |
| `ServiceInfoView` | GET, POST | Displays and processes `ServiceInfoForm()` containing service center information. |
| `ShowDocumentView` | GET, POST | Uses `DocumentInformation()` to enter document content and save the text in the database. |
| `WorkersAddView` | GET, POST | Uses `WorkersFormSet()` to display the form and add employees. |

## 5. services

This application handles services and service category management.

| View | HTTP Methods | Description |
|---|---|---|
| `DeleteCategoryOrServices` | POST | Deletes the selected service or service category. |
| `ShowAndCreateServicesWork` | GET, POST | Displays and filters services and handles service creation using `ServicesWorkForm()`. |

## 6. storage

This application handles inventory management, incoming stock, write-offs, and inventory history.

| View | HTTP Methods | Description |
|---|---|---|
| `StorageAcceptableCustomView` | GET, POST | Displays `StorageAcceptableForm()` and handles incoming inventory records in `StorageInfo`. |
| `FormRemovalCustomView` | GET | Displays `RemovalHistoryForm()` and `GarantyHistoryForm()`. |
| `StorageGarantyCustomView` | POST | Handles warranty-related stock write-offs using `GarantyHistoryForm()`. |
| `FilterHistoryCustomView` | GET | Retrieves inventory history from `HistoryStorageInfo` and applies filters. |
| `StorageCustomView` | GET | Displays current inventory records from `StorageInfo`. |
| `StorageRemovalCustomView` | POST | Handles inventory write-offs using `RemovalHistoryForm()`. |
| `CountryAutocomplete` | GET | Searches `StorageInfo` objects for autocomplete functionality in inventory operations. |

---

## Note

This documentation describes the views class-based-views on the project structure and their provided responsibilities.

It is not intended to be a complete specification of all business processes or API endpoints.
