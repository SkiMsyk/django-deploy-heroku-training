from .models import Category

def all_categories(request):
    categories = Category.objects.all().order_by('name')[:10]
    
    params = {
        'categories': categories
    }
    
    return params