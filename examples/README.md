# Examples

This folder contains example scripts demonstrating all methods for each of the 7 method types.

## Files

### 1. app_methods_example.py
Demonstrates all 6 app methods:
- `app_analyze()` - Get all data as dictionary
- `app_get_field()` - Get single field value
- `app_get_fields()` - Get multiple fields
- `app_print_field()` - Print single field to console
- `app_print_fields()` - Print multiple fields to console
- `app_print_all()` - Print all data as JSON

### 2. search_methods_example.py
Demonstrates all 6 search methods:
- `search_analyze()` - Get all search results
- `search_get_field()` - Get single field from results
- `search_get_fields()` - Get multiple fields from results
- `search_print_field()` - Print single field from results
- `search_print_fields()` - Print multiple fields from results
- `search_print_all()` - Print all results as JSON

### 3. reviews_methods_example.py
Demonstrates all 6 reviews methods:
- `reviews_analyze()` - Get all reviews
- `reviews_get_field()` - Get single field from reviews
- `reviews_get_fields()` - Get multiple fields from reviews
- `reviews_print_field()` - Print single field from reviews
- `reviews_print_fields()` - Print multiple fields from reviews
- `reviews_print_all()` - Print all reviews as JSON

### 4. developer_methods_example.py
Demonstrates all 6 developer methods:
- `developer_analyze()` - Get all developer apps
- `developer_get_field()` - Get single field from apps
- `developer_get_fields()` - Get multiple fields from apps
- `developer_print_field()` - Print single field from apps
- `developer_print_fields()` - Print multiple fields from apps
- `developer_print_all()` - Print all apps as JSON

### 5. list_methods_example.py
Demonstrates all 6 list methods:
- `list_analyze()` - Get all top chart apps
- `list_get_field()` - Get single field from apps
- `list_get_fields()` - Get multiple fields from apps
- `list_print_field()` - Print single field from apps
- `list_print_fields()` - Print multiple fields from apps
- `list_print_all()` - Print all apps as JSON

### 6. similar_methods_example.py
Demonstrates all 6 similar methods:
- `similar_analyze()` - Get all similar apps
- `similar_get_field()` - Get single field from apps
- `similar_get_fields()` - Get multiple fields from apps
- `similar_print_field()` - Print single field from apps
- `similar_print_fields()` - Print multiple fields from apps
- `similar_print_all()` - Print all apps as JSON

### 7. suggest_methods_example.py
Demonstrates all 4 suggest methods:
- `suggest_analyze()` - Get search suggestions
- `suggest_nested()` - Get nested suggestions
- `suggest_print_all()` - Print suggestions as JSON
- `suggest_print_nested()` - Print nested suggestions as JSON

### 8. Web UI (ui/ + api/)
Ships an HTML/JavaScript front-end (in `ui/`) backed by the serverless API
in `api/index.py`.  Deploy both folders to Vercel (or serve `ui/` as static
files and point the JavaScript to the API) to explore the scraper from your
browser.

## Running Examples

```bash
# Run any example
python examples/app_methods_example.py
python examples/search_methods_example.py
python examples/reviews_methods_example.py
python examples/developer_methods_example.py
python examples/list_methods_example.py
python examples/similar_methods_example.py
python examples/suggest_methods_example.py
# Launch the Vercel web UI locally
vercel dev
```

## Note

These examples are simple demonstrations. For more advanced use cases, check the documentation in the `README/` folder.
