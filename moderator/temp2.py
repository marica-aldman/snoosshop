
class ProductsView(View):
    def get(self, *args, **kwargs):
        try:
            # get the first 20 products and a count of all products
            products = Item.objects.all()[:20]
            number_products = Item.objects.all().count()
            # figure out how many pages of 20 there are
            # if there are only 20 or fewer pages will be 1

            p_pages = 1

            if number_products > 20:
                # if there are more we divide by ten
                p_pages = number_products / 20
                # see if there is a decimal
                testP = int(p_pages)
                # if there isn't an even number of ten make an extra page for the last group
                if testP != p_pages:
                    p_pages = int(p_pages)
                    p_pages += 1

            # create a list for a ul to work through

            more_products = []

            i = 0
            # populate the list with the amount of pages there are
            for i in range(p_pages):
                i += 1
                more_products.append({'number': i})

            # make search for specific product

            form = searchProductForm()

            # set current page to 1
            current_page = 1

            # set a bool to check if we are showing one or multiple categories

            multiple = True

            # set the hidden value for wether or not we have done a search

            search_type = "None"
            search_value = "None"

            context = {
                'search_type': search_type,
                'search_value': search_value,
                'multiple': multiple,
                'products': products,
                'more_categories': more_categories,
                'form': form,
                'current_page': current_page,
                'max_pages': p_pages,
            }

            return render(self.request, "moderator/mod_products.html", context)

        except ObjectDoesNotExist:
            messages.info(
                self.request, error_message_86)
            return redirect("moderator:overview")

    def post(self, *args, **kwargs):
        try:
            # where are we
            current_page = 1
            if 'current_page' in self.request.POST.keys():
                current_page = int(self.request.POST['current_page'])

            # what button did we press

            if 'search' in self.request.POST.keys() and self.request.POST['search'] != "None":
                # make a form and populate so we can clean the data
                if 'previousPage' in self.request.POST.keys() or 'nextPage' in self.request.POST.keys() or 'page' in self.request.POST.keys():
                    # we only have one type of search for this we can only get one page.
                    category_id = int(self.request.POST['search_value'])

                    if category_id != 0:
                        # next page on a single user is the same as the search for single user
                        # get the user

                        try:
                            the_category = Category.objects.get(id=category_id)

                            # there is only one
                            c_pages = 1
                            more_categories = [{'number': 1}]

                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "categoryID"

                            context = {
                                'search_type': search_type,
                                'search_value': category_id,
                                'multiple': multiple,
                                'category': the_category,
                                'more_categories': more_categories,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': c_pages,
                            }

                            return render(self.request, "moderator/mod_categories.html", context)

                        except ObjectDoesNotExist:
                            messages.info(
                                self.request, info_message_44)
                            return redirect("moderator:categories")
                    else:
                        # if the product id is 0 we are probably trying to reset the form
                        return redirect("moderator:products")

                else:
                    # make a form and populate so we can clean the data
                    form = searchCategoryForm(self.request.POST)

                    if form.is_valid():
                        # get the values
                        category_id = form.cleaned_data.get('category_id')
                        # search done on product id
                        search_value = category_id
                        # get the product
                        try:
                            category = Category.objects.get(id=category_id)
                            c_pages = 1
                            more_categories = [{'number': 1}]
                            # set current page to 1
                            current_page = 1

                            # set a bool to check if we are showing one or multiple orders

                            multiple = False

                            # set the search type

                            search_type = "categoryID"

                            context = {
                                'search_type': search_type,
                                'search_value': search_value,
                                'multiple': multiple,
                                'category': category,
                                'more_categories': more_categories,
                                'form': form,
                                'current_page': current_page,
                                'max_pages': c_pages,
                            }

                            return render(self.request, "moderator/mod_categories.html", context)

                        except ObjectDoesNotExist:
                            # most likely trying to reset the form
                            return redirect("moderator:categories")
                    else:
                        # rerender page with error message
                        # get the first 20 categories and a count of all categories
                        categories = Category.objects.all()[:20]
                        number_categories = Category.objects.all().count()
                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        c_pages = 1

                        if number_categories > 20:
                            # if there are more we divide by ten
                            c_pages = number_categories / 20
                            # see if there is a decimal
                            testC = int(c_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testC != c_pages:
                                c_pages = int(c_pages)
                                c_pages += 1

                        # create a list for a ul to work through

                        more_categories = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(c_pages):
                            i += 1
                            more_categories.append({'number': i})

                        # we already have the form

                        # set current page to 1
                        current_page = 1

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'categories': categories,
                            'more_categories': more_categories,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': c_pages,
                        }

                        if self.request.POST['category_id'] != "":
                            message.warning(
                                self.request, error_message_97)
                        return render(self.request, "moderator/mod_categories.html", context)

            elif 'nextPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                try:
                    number_categories = Category.objects.all(
                    ).count()
                    number_pages = number_categories / 20
                    if current_page < number_pages:
                        current_page += 1
                    offset = current_page * 20
                    categories = Category.objects.all()[20:offset]
                except ObjectDoesNotExist:
                    categories = {}
                    number_categories = 0

                # figure out how many pages of 20 there are
                # if there are only 20 or fewer pages will be 1

                c_pages = 1

                if number_categories > 20:
                    # if there are more we divide by ten
                    c_pages = number_categories / 20
                    # see if there is a decimal
                    testC = int(c_pages)
                    # if there isn't an even number of ten make an extra page for the last group
                    if testC != c_pages:
                        c_pages = int(c_pages)
                        c_pages += 1

                # create a list for a ul to work through

                more_categories = []

                i = 0
                # populate the list with the amount of pages there are
                for i in range(c_pages):
                    i += 1
                    more_categories.append({'number': i})

                # make search for specific order or customer

                form = searchCategoryForm()

                # set a bool to check if we are showing one or multiple orders

                multiple = True

                # set the hidden value for wether or not we have done a search

                search_type = "None"
                search_value = "None"

                context = {
                    'search_type': search_type,
                    'search_value': search_value,
                    'multiple': multiple,
                    'categories': categories,
                    'more_categories': more_categories,
                    'form': form,
                    'current_page': current_page,
                    'max_pages': c_pages,
                }

                return render(self.request, "moderator/mod_categories.html", context)

            elif 'previousPage' in self.request.POST.keys():
                # get what type of search
                search_type = self.request.POST['search']

                # check what kind of search
                if current_page > 2:

                    try:
                        if current_page > 1:
                            current_page -= 1
                        offset = current_page * 20
                        categories = Category.objects.all()[20:offset]
                        number_categories = Category.objects.all(
                        ).count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        c_pages = 1

                        if number_categories > 20:
                            # if there are more we divide by ten
                            c_pages = number_categories / 20
                            # see if there is a decimal
                            testP = int(c_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testP != c_pages:
                                c_pages = int(c_pages)
                                c_pages += 1

                        # create a list for a ul to work through

                        more_categories = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(c_pages):
                            i += 1
                            more_categories.append({'number': i})

                        # make search for specific order or customer

                        form = searchCategoryForm()

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'categories': categories,
                            'more_categories': more_categories,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': c_pages,
                        }

                        return render(self.request, "moderator/mod_categories.html", context)

                    except ObjectDoesNotExist:
                        messages.warning(
                            self.request, error_message_98)
                        return redirect("moderator:categories")

                else:

                    try:
                        if current_page > 1:
                            current_page -= 1
                        categories = Category.objects.all()[:20]
                        number_categories = Category.objects.all(
                        ).count()

                        # figure out how many pages of 20 there are
                        # if there are only 20 or fewer pages will be 1

                        c_pages = 1

                        if number_categories > 20:
                            # if there are more we divide by ten
                            p_pages = number_categories / 20
                            # see if there is a decimal
                            testC = int(c_pages)
                            # if there isn't an even number of ten make an extra page for the last group
                            if testC != c_pages:
                                c_pages = int(c_pages)
                                c_pages += 1

                        # create a list for a ul to work through

                        more_categories = []

                        i = 0
                        # populate the list with the amount of pages there are
                        for i in range(c_pages):
                            i += 1
                            more_categories.append({'number': i})

                        # make search for specific order or customer

                        form = searchCategoryForm()

                        # set a bool to check if we are showing one or multiple orders

                        multiple = True

                        # set the hidden value for wether or not we have done a search

                        search_type = "None"
                        search_value = "None"

                        context = {
                            'search_type': search_type,
                            'search_value': search_value,
                            'multiple': multiple,
                            'categories': categories,
                            'more_categories': more_categories,
                            'form': form,
                            'current_page': current_page,
                            'max_pages': c_pages,
                        }

                        return render(self.request, "moderator/mod_categories.html", context)

                    except ObjectDoesNotExist:
                        messages.warning(
                            self.request, error_message_99)
                        return redirect("moderator:categories")
            elif 'delete' in self.request.POST.keys():
                if 'id' in self.request.POST.keys():

                    category_id = int(self.request.POST['id'])
                    category = Category.objects.get(id=category_id)
                    category.delete()

                    messages.info(
                        self.request, info_message_47)
                    return redirect("moderator:categories")
                else:
                    return redirect("moderator:categories")
            else:
                return redirect("moderator:categories")

        except ObjectDoesNotExist:
            messages.warning(
                self.request, error_message_100)
            return redirect("moderator:overview")
