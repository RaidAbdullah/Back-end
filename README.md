# Flask Backend API for Flutter App

This is a Flask-based REST API backend designed to work with a Flutter frontend application.

## Setup Instructions

1. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- GET `/api/health`
  - Returns the API status

### Example Endpoints
- GET `/api/example`
  - Returns example data
- POST `/api/example`
  - Accepts JSON data
  - Returns confirmation of received data

## Flutter Integration

In your Flutter application, you can use these endpoints like this:

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

// Get data example
Future<void> getData() async {
  final response = await http.get(Uri.parse('http://localhost:5000/api/example'));
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    // Process your data here
  }
}

// Post data example
Future<void> postData(Map<String, dynamic> data) async {
  final response = await http.post(
    Uri.parse('http://localhost:5000/api/example'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode(data),
  );
  if (response.statusCode == 201) {
    // Handle successful response
  }
}
