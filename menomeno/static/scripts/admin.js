// This client is entirely based on the one provided in the course material
// I have generalized it to work with diverse collection+json objects

"use strict";

// TODO:
// Hardcoded method information, because of collection+json limitations
const PUT_ALLOWED = ["cities/", "organizers/", "events/", "venues/"];
const POST_ALLOWED = ["cities/", "events/", "venues/"];
const DELETE_ALLOWED = ["events/"];

const DEBUG = true;
const COLLECTIONJSON = "application/vnd.collection+json";
const PLAINJSON = "application/json";

// Dynamically set the resource location based on route used
let myPath = window.location.pathname;
let resurssi = "http://localhost:5000/api";
const domain = "http://localhost:5000";
if (myPath.endsWith("venues/")) {
    resurssi += "/cities" + window.location.pathname;
} else {
    resurssi += myPath;
}

// Pass template data as global
let templ = {};

// Function to render error alerts
function renderError(jqxhr) {
    try {
        let msg = jqxhr.responseJSON["collection"]["error"]["message"];
        $("div.notification").html("<p class='alert alert-warning'>" + msg + "</p>");    
    } catch(err) {
        $("div.notification").html("<p class='alert alert-warning'>Undefined error</p>");
    }
}

// Function to render other than error alerts
function renderMsg(msg) {
    $("div.notification").html("<p class='alert alert-primary'>" + msg + "</p>");
}

// Helper function to follow links without standard HTTP calls
function followLink(event, a, renderer) {
    event.preventDefault();
    $("div.notification").empty();
    getResource($(a).attr("href"), renderer);
}

// General ajax function to render a resource
function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

// Function to append a row of data to table
function appendItemRow(body) {
    $(".table tbody").append(dataRow(body));
}

// Callback function executed after successful submission.
// NOTE: every POST and PUT will render the item in question
// and not the collection of items even in the case where
// the POST initiated from collection.
function getSubmittedItem(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    console.log("We got response header:")
    console.log(href); 
    if (href) {
        //getResource(href, appendItemRow);
        getResource(href, renderItem);
    }
}

// Helper function making an Ajax call to send data to server
function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}

// Function that handles submitting form data
function submitItem(event) {
    event.preventDefault();
    $("div.notification").empty();
    let data = [];
    let form = $("div.form form");
    templ.template.data.forEach( function (item) {
        let itemvalue = $("input[name='" + item.name + "']").val();
        data.push({"name": item.name, 
                    "value": itemvalue,
                    "prompt": item.prompt
                });
    });
    templ = { "template": {"data": data} };
    sendData(form.attr("action"), form.attr("method"), templ, getSubmittedItem);
}

// General function for rendering form based on collection+json data
function renderItemForm(ctrl, method) {
    let form = $("<form>");
    let fields = [];
    ctrl.template.data.forEach( function (item) {
        fields.push([item.name, item.value, item.prompt]);
    });

    if (method == 'post') {
        form.attr("action", domain + ctrl.href);
    } else if (method == 'put') {
        form.attr("action", domain + ctrl.items[0].href);
    }

    form.attr("method", method);
    templ = { "template": {"data": ctrl.template.data} };
    form.submit(submitItem);
    fields.forEach(function (item) {
        form.append("<label>" + item[2] + " : </label");
        form.append(" <input type='text' name='" + item[0] + "'> <br /> ");
    });

    form.append("<input type='submit' class='btn btn-primary' name='submit' value='Submit'>");
    $("div.form").html(form);
}

// Function to render a single item in collection+json object
function renderItem(body) {
    let navistring = "";
    
    try {
        navistring += "<a href='" + body.collection.href +
        "' onClick='followLink(event, this, renderCollection)'>Collection</a>"
    } catch {}

    try {
        body.collection.links.forEach ( function (item) {
            // This is a terrible hack manually checking
            // if we should include links to collections or single items:
            if (['cities/', 'events/', 'venues/'].indexOf(item.href.slice(-7)) >= 0) {
                navistring += " | <a href='" + item.href +
                        "' onClick='followLink(event, this, renderCollection)'>" +
                        item.prompt + "</a>"
            } else if (item.prompt == "Link to profile") {
                navistring += " | <a href='" + item.href + "'>" +
                item.prompt + "</a>"
            } else {
                navistring += " | <a href='" + item.href +
                "' onClick='followLink(event, this, renderItem)'>" +
                item.prompt + "</a>"         
            }
        });    
    } catch(err) {}

    console.log(body.collection.items[0].links);
    body.collection.items[0].links.forEach ( function (item) {
        navistring += " | <a href='" + item.href +
                    "' onClick='followLink(event, this, renderCollection)'>" +
                    item.prompt + "</a>"
    });

    $("div.navigation").empty();
    $("div.navigation").html(navistring);    
    $(".table thead").empty();
    $(".table tbody").empty();
    renderItemForm(body["collection"], "put");
    body.collection.template.data.forEach ( function (item) {
        $("input[name='" + item.name + "']").val(item.value);
    });
}

function renderAfterDelete(body) {
    getResource(resurssi, renderCollection);
    $("div.notification").empty();
    $("div.notification").html("<p class='alert alert-primary'>Succesfully deleted event</p>");   
}

function deleteItem(body) {
    resurssi = domain + body.collection.href;
    sendData(body.collection.items[0].href, "delete", "", renderAfterDelete);
}

// Function for adding a row of data to table
function dataRow(item, deleteEnabled) {
    let link = "<a href='" + item["href"] +
                "' onClick='followLink(event, this, renderItem)'>edit</a>";
    let delete_link = "<a href='" + item["href"] +
    "' onClick='followLink(event, this, deleteItem)'>Delete</a>";

    let row_string = "<tr>";
    item.data.forEach(function (data) {
        row_string += "<td>" + data.value + " ";
    })
    if (deleteEnabled) {
        row_string += "</td><td>" + link + "</td><td class='btn btn-danger'>" + delete_link + "</td></tr>"
    } else {
        row_string += "</td><td>" + link + "</td><td>Not allowed</td></tr>"
    }
    return row_string;
    }

// Function for rendering collection+json collections
function renderCollection(body) {

    let deleteEnabled = false;
    if (body.collection.href.endsWith('events/')) {
        deleteEnabled = true;
    }

    $("div.navigation").empty();
    $("div.tablecontrols").empty();

    let navistring = "";
    try {
        navistring += "<a href='" + body.collection.href +
        "' onClick='followLink(event, this, renderCollection)'>Collection</a>"
    } catch {}

    body.collection.links.forEach ( function (item) {
        // This is a terrible hack manually checking
        // if we should include links to collections or single items:
        if (['cities/', 'events/', 'venues/'].indexOf(item.href.slice(-7)) >= 0) {
            navistring += " | <a href='" + item.href +
                    "' onClick='followLink(event, this, renderCollection)'>" +
                    item.prompt + "</a>"
        } else if (item.prompt == "Link to profile") {
            navistring += " | <a href='" + item.href + "'>" +
            item.prompt + "</a>"
        } else {
            navistring += " | <a href='" + item.href +
            "' onClick='followLink(event, this, renderItem)'>" +
            item.prompt + "</a>"         
        }
    });

    $("div.navigation").empty();
    $("div.navigation").html(navistring);   
    // Set header row columns to data item prompts
    let header_row = "<tr>";
    try {
        body.collection.items[0].data.forEach(function (item) {
            header_row += "<th>" + item.prompt + "</th>";
        });
        header_row += "<th>Item link</th><th>delete!</th></tr>";
        $(".table thead").html(header_row);
        let tbody = $(".table tbody");
        tbody.empty();
        body.collection.items.forEach(function (item) {
            tbody.append(dataRow(item, deleteEnabled));
        });    
    } catch(err) {
        $("div.notification").html("No items in this collection");
    }
    renderItemForm(body["collection"], "post");
}

// Function to call when ready to start processsing
$(document).ready(function () {
    getResource(resurssi, renderCollection);
});