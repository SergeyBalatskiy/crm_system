# Django Views Documentation

[Русский](VIEWS.md) | [English](VIEWS.en.md)

Документация Django Views проекта CRM System.

В этом файле описаны основные представления Django, HTTP-методы и их назначение.

## Содержание

- [auth_registration](#1-auth_registration)
- [finance](#2-finance)
- [orders](#3-orders)
- [profile_user](#4-profile_user)
- [services](#5-services)
- [storage](#6-storage)

---

## 1. auth_registration

Приложение отвечает за регистрацию и авторизацию пользователей.

| View | HTTP Methods | Описание |
|---|---|---|
| `RegisterView` | GET, POST | Отображает форму регистрации и обрабатывает создание нового пользователя с помощью `CustomUserCreationForm`. |
| `CustomLoginView` | GET, POST | Отображает форму авторизации и выполняет вход пользователя с помощью `LoginForm`. |
| `ShowForm` | GET | Отображает формы входа и регистрации. |

## 2. finance

Приложение отвечает за финансовые операции и учёт денежных средств.

| View | HTTP Methods | Описание |
|---|---|---|
| `BuyFinanceCustomView` | POST | Создаёт финансовую операцию категории «Other > Income» с использованием `SellCustomForm()`. |
| `SellFinanceCustomView` | POST | Создаёт финансовую операцию категории «Other > Expense» с использованием `BuyCustomForm()`. |
| `MainCashAndHistoryView` | GET | Отображает баланс сервисного центра и историю финансовых операций с фильтрацией записей. |
| `InsertCashInBalance` | GET, POST | Отображает `InsertCashForm()` и обрабатывает создание финансовой операции категории «Product sale». |
| `ShowOthersCustomView` | GET | Отображает формы `BuyCustomForm()` и `SellCustomForm()`. |
| `CountryAutocomplete` | GET | Выполняет поиск и фильтрацию объектов `StorageInfo` для автодополнения поля. |

## 3. orders

Приложение отвечает за управление заказами, информацией о клиентах, услугами в заказах, оплатами и документами.

| View | HTTP Methods | Описание |
|---|---|---|
| `ChangeStatusOrder` | GET, POST | Отображает доступные статусы и сохраняет выбранный статус заказа. |
| `ShowClientOrder` | GET, POST | Отображает информацию о существующем заказе с использованием `FormsForOrder` и JSON-поля `json_forms`. |
| `DeleteServicesInOrder` | POST | Удаляет существующую работу, связанную с заказом. |
| `CountDsc` | POST | Рассчитывает скидку на основе общей стоимости заказа. |
| `FindClientInformation` | GET | Выполняет поиск существующих клиентов в модели `Client`. |
| `ShowFormForOrder` | GET, POST | Получает данные из базы данных и отображает текущие поля формы заказа. |
| `GetTotalCount` | GET | Возвращает общую стоимость связанных с заказом элементов. |
| `ShowAndPayView` | POST | Получает сумму и тип оплаты, создаёт запись `FinanceHistoryInfo`, обновляет баланс и формирует документ. |
| `PrintSelectedDocument` | GET, POST | Заполняет HTML-шаблон документа фактическими данными и отправляет сформированный документ пользователю. |
| `OrdersDetailsAutocomplete` | GET | Выполняет поиск объектов `StorageInfo` для автодополнения при работе с заказами. |
| `ServicesSelectAutocomplete` | GET | Выполняет поиск услуг в `ServicesInfo` для автодополнения. |
| `ServiceWorkCreate` | GET, POST | Отображает `WorkCreatingForm()` и обрабатывает создание рабочих элементов, связанных с заказом. |
| `FindWorkersInformation` | GET | Получает информацию о сотрудниках из `WorkersInfo`. |
| `ShowAndFilterOrders` | GET | Отображает список заказов и предоставляет возможности фильтрации и поиска. |

## 4. profile_user

Приложение отвечает за профиль пользователя, информацию о сервисном центре, сотрудников и управление документами.

| View | HTTP Methods | Описание |
|---|---|---|
| `ShowAdoptionView` | GET, POST | Отображает `DocumentInfoForm()` и обрабатывает создание документа о принятии. |
| `BackupDocumentView` | GET | Восстанавливает выбранный документ до стандартного состояния. |
| `ShowCancellView` | GET, POST | Использует `DocumentInfoForm()` для создания документа об отказе или отмене. |
| `ShowCategoriesView` | GET, POST | Отображает и обрабатывает создание категорий статусов `StatusCategory`. |
| `ChangePersonalInformationView` | GET, POST | Отображает личную информацию текущего пользователя и обрабатывает её редактирование. |
| `ShowCompleteView` | GET, POST | Использует `DocumentInfoForm()` для создания документа о выполненных работах. |
| `CreateNewFormInCategory` | GET, POST | Обрабатывает JSON-данные формы, сохраняет форму и отображает окно её создания. |
| `DeleteCustomForm` | POST | Удаляет пользовательскую форму из `FormsForOrder`. |
| `FormsForOrdersEdit` | GET, POST | Отображает активные формы и обрабатывает добавление, удаление и изменение их порядка в JSON. |
| `ShowGarantyView` | GET, POST | Использует `DocumentInfoForm()` для создания гарантийного документа. |
| `EditIndividualCenterForm` | GET, POST | Отображает форму автоматического ответа и сохраняет её данные в JSON. |
| `UserProfileView` | GET | Отображает профиль пользователя, фильтрует финансовые операции и передаёт набор данных для JavaScript. |
| `ServiceInfoView` | GET, POST | Отображает и обрабатывает форму `ServiceInfoForm()` с информацией о сервисном центре. |
| `ShowDocumentView` | GET, POST | Использует `DocumentInformation()` для добавления содержимого документа и сохранения текста в базе данных. |
| `WorkersAddView` | GET, POST | Использует `WorkersFormSet()` для отображения формы и добавления сотрудников. |

## 5. services

Приложение отвечает за управление услугами и категориями услуг.

| View | HTTP Methods | Описание |
|---|---|---|
| `DeleteCategoryOrServices` | POST | Удаляет выбранную услугу или категорию услуг. |
| `ShowAndCreateServicesWork` | GET, POST | Отображает список услуг, выполняет фильтрацию и обрабатывает создание услуги с помощью `ServicesWorkForm()`. |

## 6. storage

Приложение отвечает за складской учёт, поступление товаров, списания и историю складских операций.

| View | HTTP Methods | Описание |
|---|---|---|
| `StorageAcceptableCustomView` | GET, POST | Отображает `StorageAcceptableForm()` и обрабатывает поступление товаров с созданием записей в `StorageInfo`. |
| `FormRemovalCustomView` | GET | Отображает формы `RemovalHistoryForm()` и `GarantyHistoryForm()`. |
| `StorageGarantyCustomView` | POST | Обрабатывает списание товаров по гарантии с использованием `GarantyHistoryForm()`. |
| `FilterHistoryCustomView` | GET | Получает историю складских операций из `HistoryStorageInfo` и выполняет фильтрацию. |
| `StorageCustomView` | GET | Отображает текущие складские остатки из `StorageInfo`. |
| `StorageRemovalCustomView` | POST | Обрабатывает списание товаров с использованием `RemovalHistoryForm()`. |
| `CountryAutocomplete` | GET | Выполняет поиск объектов `StorageInfo` для автодополнения при работе со складом. |

---

## Примечание

Документация описывает назначение классовых представлений на основе текущей структуры проекта и их реализованной логики!

Она не является полной спецификацией бизнес-процессов или API.
