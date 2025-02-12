# Invoice managements

A Django-based invoice management API to create, update, delete, and manage invoices and related services.

## Setup Instructions

Follow the steps below to set up and run the project locally.

### 1. **Clone the Repository**
Clone the project to your local machine:
```bash
git clone https://github.com/victor90braz/django-invoice-management-api.git
cd Inmatic
```

### 2. **Set Up the Virtual Environment**
If you haven't set up a virtual environment yet, do so by running:
```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- **Mac/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. **Install Dependencies**
Install the required dependencies using `pip`:
```bash
pip install -r requirements.txt
```

### 4. **Create and Apply Migrations**
After setting up the environment and installing dependencies, apply the migrations to set up the database schema:
```bash
python manage.py migrate
```

### 5. **Create a Superuser**
To access the Django admin, you'll need to create a superuser:
```bash
python manage.py createsuperuser
```
Follow the prompts to enter the superuser's username, email, and password.

### 6. **Run the Development Server**
Start the development server to run the project locally:
```bash
python manage.py runserver
```
Access the project at `http://127.0.0.1:8000/` in your browser.

### 7. **Access the Django Admin Panel**
Once the server is running, you can access the admin panel at `http://127.0.0.1:8000/admin`. 

### 8. **Testing the Project**
Run the tests to ensure everything is working as expected:
```bash
python manage.py test InvoicesAccounting.tests.unit
```

### 9. **Test Coverage**
Run tests with coverage:
```bash
python -m coverage run manage.py test InvoicesAccounting.tests.unit
```
Generate a report:
```bash
python -m coverage report
```
Generate an HTML report (optional):
```bash
python -m coverage html
```

---

## Features

- Create, update, and delete invoices.
- Filter invoices based on state and date range.
- Generate accounting entries for invoices.

---

## Validation and Serializer

### 1. **Validation Rules in the View**
In the view handling the invoice creation, we apply validation rules using Django’s `Model.clean()` method. This method checks if the data is valid and raises validation errors when needed. Additionally, in the serializer, custom validation checks are done.

Here's how the validation works:

- When the `POST` request is made to create an invoice, the data is first validated by the `ValidateInvoice` serializer.
- If the `base_value`, `vat`, or `total_value` is missing or invalid, the serializer raises a validation error.
- The `date` field is explicitly required. If it is missing or invalid, a `ValidationError` is raised with a relevant message.

### 2. **How the Serializer Works**
The `ValidateInvoice` serializer uses Django’s `ModelSerializer` to automatically generate fields based on the `InvoiceModel` fields. Here's how it works:

- **Model Fields**: All fields defined in the `InvoiceModel` are automatically included in the serializer.
- **Validation**: In the `validate` method, custom validation is applied to ensure the `date` field is provided and that the `base_value` and `vat` are non-negative. The model’s `clean()` method is called to handle additional validations like checking if `total_value` matches the sum of `base_value` and `vat`.
  
  ```python
  def validate(self, data):
      if 'date' not in data or not data['date']:
          raise serializers.ValidationError({'date': 'This field is required.'})

      invoice = InvoiceModel(**data)
      try:
          invoice.clean()  
      except ValidationError as e:
          raise serializers.ValidationError(e.message_dict)

      return data
  ```

### 3. **Model's `clean()` Method**
- The `InvoiceModel`'s `clean()` method checks if the `base_value` is greater than zero, the `vat` is non-negative, and the `total_value` is valid. If any of these conditions fail, the method raises a `ValidationError`.

```python
def clean(self):
    errors = {}

    if self.base_value <= 0:
        errors["base_value"] = "Base value must be greater than zero."

    if self.vat < 0:
        errors["vat"] = "VAT cannot be negative."

    if self.total_value <= 0:
        errors["total_value"] = "Total value must be greater than zero."

    expected_total = self.base_value + self.vat
    if self.total_value != expected_total:
        errors["total_value"] = f"Total value must be {expected_total}."

    if errors:
        raise ValidationError(errors)
```

### 4. **Example Flow**:
- When a `POST` request is made to create an invoice:
  1. The serializer first validates the incoming data. 
  2. The `validate()` method ensures the `date` is present and checks other business rules.
  3. If the data is valid, the `InvoiceModel` is created or updated.

---

## Troubleshooting

- **Missing Migrations**: If you face issues related to migrations, run `python manage.py makemigrations` and then `python manage.py migrate` again.

- **Admin Panel Not Accessible**: Ensure you created the superuser correctly. If you encounter a `404` error when accessing the admin, double-check your URL configuration in `urls.py`.

---

