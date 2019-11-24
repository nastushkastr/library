"use strict";

document.querySelectorAll("form._add_to_cart").forEach(element => {
    let count = element.getElementsByTagName("input")[0].value;
    element.querySelectorAll("a").forEach((el) => {
        el.addEventListener("click", (event) => {
            console.log("HUI");
            event.preventDefault();
            if (count > 0) {
                $.ajax({
                    url: `/cart?ed_id=${element.id}&count=${count}`,
                    method: "POST",
                    success: () => {
                        alert("Книга успешно добавлена в корзину");
                    }
                });
            } else {
                alert(`Количество должно быть положительным`);
            }
        });
    });
});

document.querySelectorAll("form._count_in_card").forEach(element => {
    element.querySelectorAll("input").forEach((el) => {
        el.addEventListener("change", (event) => {
            event.preventDefault();
        });
        el.addEventListener("focusout", (event) => {
            $.ajax({
                url: `/cart?ed_id=${element.id}&count=${event.target.value}`,
                method: "PUT"
            });
        });
    });
    element.querySelectorAll("a").forEach((el) => {
        el.addEventListener("click", (event) => {
            event.preventDefault();
            if (confirm("Вы действительно хотите удалить?"))
            {
                $.ajax({
                    url: `/cart?ed_id=${element.id}`,
                    method: "DELETE",
                    complete: (xhr, text) => {
                        if (xhr.status == 200) {
                            element.parentNode.parentNode.remove();
                        }
                    }
                });
            }
        });
    });
});



document.querySelectorAll("button._order").forEach(element => {
    element.addEventListener("click", (event) => {
        $.ajax({
            url: '/order',
            method: "POST",
            complete: (xhr, text) => {
                if (xhr.status != 200) {
                    alert("Что-то пошло не так(");
                } else {
                    document.querySelectorAll("tr._cart").forEach(element => {
                        element.remove();
                    })
                }
            }
        });
    })
});

let deleteHandler = (event) => {
    event.preventDefault();
    let row = event.target.parentNode.parentNode.parentNode;
    if (confirm("Вы действительно хотите удалить?")) {
        $.ajax({
            url: `/books/${row.id}`,
            method: "DELETE",
            success: () => {
                row.remove();
            }
        });
    }
}

document.querySelectorAll("form._book_delete").forEach((element) => {
    element.querySelectorAll("button").forEach((el) => {
        el.addEventListener("click", deleteHandler);
    });
});

