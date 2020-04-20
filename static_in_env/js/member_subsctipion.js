class Product {
    constructor(nop, product_choices) {
        // variables
        var new_nop = nop + 1;
        var product_name = "product" + new_nop;
        var product_id = "id_product" + new_nop;
        var amount_name = "amount" + new_nop;
        var amount_id = "id_amount" + new_nop;
        // product section
        // static title
        product_title = document.createTextNode("Vara:");
        product_title_td = document.createElement("td");
        product_title_td.setAttribute("class", "w-25");
        product_title_td.appendChild(product_title);
        //product selection
        product_field = document.createElement("select");
        product_field.setAttribute("name", product_name);
        product_field.setAttribute("id", product_id);
        // populate select
        for (x in product_choices) {
            product_choice_text = document.createTextNode(x.title)
            product_choice = document.createElement("option")
            product_choice.appendChild(product_choice_text);
            product_choice.setAttribute("value", x.id);
            product_field.appendChild(product_choice);
        }
        product_field_td = document.createElement("td");
        product_field_td.appendChild(product_field);
        // remove button
        remove_button_text = document.createTextNode("X");
        remove_button = document.createElement("button");
        remove_button.appendChild(remove_button_text);
        remove_button.setAttribute("class", "");
        remove_button.addEventListener("click", remove_product(new_nop));
        remove_button_td = document.createElement("td");
        remove_button_td.appendChild(remove_button);
        // product line
        product_tr = document.createElement("tr");
        product_tr.appendChild(product_title_td);
        product_tr.appendChild(product_field_td);
        product_tr.appendChild(remove_button_td);
        //amount section
        amount_title = document.createTextNode("Mängd:");
        amount_title_td = document.createElement("td");
        amount_title_td.appendChild(amount_title);
        amount_title_td.setAttribute("class", "w-25");
        amount_field = document.createElement("input");
        amount_field.setAttribute("id", amount_id);
        amount_field.setAttribute("type", "number");
        amount_field.setAttribute("min", "1");
        amount_field.setAttribute("name", amount_name);
        amount_field_td = document.createElement("td");
        amount_field_td.appendChild(amount_field);
        amount_extra_td_text = document.createTextNode(" ");
        amount_extra_td = document.createElement("td");
        amount_extra_td.appendChild(amount_extra_td_text);
        //amount line
        amount_tr = document.createElement("tr");
        amount_tr.appendChild(amount_title_td);
        amount_tr.appendChild(amount_field_td);
        amount_tr.appendChild(amount_extra_td);
        //table parts
        table_body = document.createElement("tbody");
        table_body.appendChild(product_tr);
        table_body.appendChild(amount_tr);
        table = document.createElement("table");
        table.setAttribute("class", "table table-striped table-hover w-100  mb-2");
        table.setAttribute("id", product_name);
        table.appendChild(table_body);
    }
}

function add_product() {
    base_div = document.getElementById('products')
    nop = document.getElementById("number_of_products").nodeValue;
    product_choices = document.getElementById("list_of_products").nodeValue;
    new_product = new Product(nop, product_choices);
    console.log(new_product);
    button = document.getElementById("add");
    base_div.insertBefore(button, new_product)
    return false;
}

function remove_product(id) {
    element = document.getElementById(id)
    element.remove()
    return false;
}