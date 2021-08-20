from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product
from basket.views import alter_product

# Create your views here.
consoles = ["No Specific Console", "Nintendo 64", "NES", "SNES"]
categories = ["All", "Consoles", "Games", "Accessories", "Bundles"]


def all_products(request):
    """ This will display just the all products """

    products = Product.objects.all()

    search = None
    search_num = None
    ids = [0, 0]
    query = None
    sortkey = None

    if request.GET:
        if "search" in request.GET:
            query = [request.GET["c"], request.GET["q"], request.GET["f"]]
            if query[2] != "":
                if query[2] == "A-Z":
                    sortkey = f'{"lower_name"}'
                    products = products.annotate(lower_name=Lower("name"))
                if query[2] == "Z-A":
                    sortkey = f'-{"lower_name"}'
                    products = products.annotate(lower_name=Lower("name"))
                if query[2] == "Ascending Price":
                    sortkey = f'{"price"}'
                if query[2] == "Decending Price":
                    sortkey = f'-{"price"}'
                if query[2] == "Rating":
                    sortkey = f'{"rating"}'
                if sortkey is not None:
                    products = products.order_by(sortkey)
            if not query:
                return redirect("home")

            if query[0] in consoles:
                ids[0] = consoles.index(query[0])
            else:
                ids[0] = 0
                query[0] = "No Specific Console"
            if query[1] in categories:
                ids[1] = categories.index(query[1])
            else:
                ids[1] = 0
                query[1] = "All"

            if query[0] == "No Specific Console" and query[1] != "All":
                queries = Q(category=ids[1])
            elif query[1] == "All" and query[0] != "No Specific Console":
                queries = Q(console=ids[0])
            else:
                queries = Q(console=ids[0]) & Q(category=ids[1])

            if (query[0] != "No Specific Console"):
                products = products.filter(queries)
            else:
                products = products
        else:
            search = request.GET["search"]
            queries = Q(
                name__icontains=search) | Q(description__icontains=search)
            products = products.filter(queries)
            search_num = len(products)

    context = {
        "products": products,
        "search_q": search,
        "return_num": search_num,
    }

    return render(request, "products/products.html", context)


def product_detail(request, product_pk):
    """ This will display the page of the item that has been selected."""

    products = get_object_or_404(Product, pk=product_pk)
    add_msg = ""

    basket = request.session.get("basket", {})

    if request.GET:
        if "add" in request.GET:
            alter_product(request, True, product_pk)
            add_msg = "This product has been added to your basket."
        elif "remove" in request.GET:
            alter_product(request, False, product_pk)
            add_msg = "This product has been removed from your basket."

    context = {
        "products": products,
        "add_msg": add_msg,
        "basket_contents": basket
    }

    return render(request, "products/product.html", context)
