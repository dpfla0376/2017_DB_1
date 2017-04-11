/**
 * Created by 상원 on 2017-04-08.
 * haha
 */
function changeTrColor(tdObj, oldColor, newColor) {
    tdObj.style.backgroundColor = newColor;
    tdObj.onmouseout = function () {
        tdObj.style.backgroundColor = oldColor;
    }
}
function td_click_detail_server(tdObj) {
    var txt = tdObj.text;
    location.href = "/dbApp/server/detail/?data=" + txt;
}
function td_click_detail_rack(tdObj) {
    var txt = tdObj.text;
    location.href = "/dbApp/rack/detail/?data=" + txt;
}
function td_click_detail_asset(tdObj) {
    var txt = tdObj.text;
    location.href = "/dbApp/asset/detail/?data=" + txt;
}
function td_click_detail_switch(tdObj) {
    var txt = tdObj.text;
    location.href = "/dbApp/switch/detail/?data=" + txt;
}
function td_click_detail_service(tdObj) {
    var txt = tdObj.text;
    location.href = "/dbApp/service/detail/?data=" + txt;
}

function td_click_delete_asset(assetNum) {
    myConfirm("삭제하시겠습니까?", function () {
        deleteRequest("/dbApp/asset/delete/", assetNum, "asset-id-");
    });
}

function td_click_delete_server(manageNum) {
    myConfirm("삭제하시겠습니까?", function () {
        deleteRequest("/dbApp/server/delete/", manageNum, "one-asset-id-");
    });
}

function td_click_delete_storage(manageNum) {
    myConfirm("삭제하시겠습니까?", function () {
        deleteRequest("/dbApp/storage/delete/", manageNum, "one-asset-id-");
    });
}

function td_click_delete_rack(manageNum) {
    myConfirm("삭제하시겠습니까?", function () {
        deleteRequest("/dbApp/rack/delete/", manageNum, "one-asset-id-");
    });
}

function td_click_delete_switch(assetNum) {
    myConfirm("삭제하시겠습니까?", function () {
        deleteRequest("/dbApp/switch/delete/", assetNum, "one-asset-id-");
    });
}

function deleteRequest(url, id, id_name) {
    $.ajax({
        url: url + id,
        success: function (result) {
            $("#" + id_name + id).remove();
        },
        fail: function (error) {
            alert("fail");
        }
    });
}

function myConfirm(message, callback) {
    if (confirm(message)) {
        callback();
    }
}
function td_click_edit(type, id) {

    if (type == "asset") {
        var acq_date = document.getElementById("acq-date-" + id);
        var name = document.getElementById("name-" + id);
        var standard = document.getElementById("standard-" + id);
        var acq_cost = document.getElementById("acq-cost-" + id);
        var purchase = document.getElementById("purchase-" + id);
        var maintenance = document.getElementById("maintenance-" + id);

        var acq_date_data = acq_date.innerHTML;
        var name_data = name.innerHTML;
        var standard_data = standard.innerHTML;
        var acq_cost_data = acq_cost.innerHTML;
        var purchase_data = purchase.innerHTML;
        var maintenance_data = maintenance.innerHTML;

        acq_date.innerHTML = "<input type='date' id='acq-date-input-" + id + " value='" + acq_date_data + "'>";
        name.innerHTML = "<input type='text' id='name-input-" + id + "' value='" + name_data + "'>";
        standard.innerHTML = "<input type='text' id='standard-input-" + id + "' value='" + standard_data + "'>";
        acq_cost.innerHTML = "<input type='number' id='acq-cost-input-" + id + "' value='" + acq_cost_data + "'>";
        purchase.innerHTML = "<input type='text' id='purchase-input-" + id + "' value='" + purchase_data + "'>";
        maintenance.innerHTML = "<input type='number' id='maintenance-input-" + id + "' value='" + maintenance_data + "'>";
    }
    else if (type == "server") {

        var manage_spec = document.getElementById("manage-spec-" + id);
        var core = document.getElementById("core-" + id);
        var ip = document.getElementById("ip-" + id);
        var onoff = document.getElementById("onoff-" + id);
        var size = document.getElementById("size-" + id);
        var location = document.getElementById("location-" + id);

        var manage_spec_data = manage_spec.innerHTML;
        var core_data = core.innerHTML;
        var ip_data = ip.innerHTML;
        var onoff_data = onoff.innerHTML;
        var size_data = size.innerHTML;
        var location_data = size.innerHTML;

        manage_spec.innerHTML = "<input type='text' id='manage-spec-input-" + id + "' value='" + manage_spec_data + "'>";
        core.innerHTML = "<input type='number' id='core-input-" + id + "' value='" + core_data + "'>";
        ip.innerHTML = "<input type='text' id='ip-input-" + id + "' value='" + ip_data + "'>";
        onoff.innerHTML = "<input type='text' id='onoff-input-" + id + "' value='" + onoff_data + "'>";
        size.innerHTML = "<input type='number' id='size-input-" + id + "' value='" + size_data + "'>";
        location.innerHTML += "<input type='number' id='location-input-" + id + "' value='" + location_data + "'>"+"<input type='number' id='location-in-input-" + id + "' value='" + location_data + "'>"+"<input type='number' id='location-at-input-" + id + "' value='" + location_data + "'>";

    }
    else if (type == "storage") {
        var manage_spec = document.getElementById("manage-spec-" + id);
        var standard = document.getElementById("standard-" + id);
        var location = document.getElementById("location-" + id);

        var manage_spec_data = manage_spec.innerHTML;
        var location_data = location.innerHTML;
        var standard_data = standard.innerHTML;

        manage_spec.innerHTML = "<input type='text' id='manage-spec-input-" + id + "' value='" + manage_spec_data + "'>";
        location.innerHTML = "<input type='text' id='location-input-" + id + "' value='" + location_data + "'>";
        standard.innerHTML = "<input type='text' id='standard-input-" + id + "' value='" + standard_data + "'>";
    }
    else if (type == "switch") {

        var manage_spec = document.getElementById("manage-spec-" + id);
        var ip = document.getElementById("ip-" + id);
        var onoff = document.getElementById("onoff-" + id);
        var size = document.getElementById("size-" + id);

        var manage_spec_data = manage_spec.innerHTML;
        var ip_data = ip.innerHTML;
        var onoff_data = onoff.innerHTML;
        var size_data = size.innerHTML;

        manage_spec.innerHTML = "<input type='text' id='manage-spec-input-" + id + "' value='" + manage_spec_data + "'>";
        ip.innerHTML = "<input type='text' id='ip-input-" + id + "' value='" + ip_data + "'>";
        onoff.innerHTML = "<input type='text' id='onoff-input-" + id + "' value='" + onoff_data + "'>";
        size.innerHTML = "<input type='number' id='size-input-" + id + "' value='" + size_data + "'>";
    }
    else if (type == "rack") {
        var manage_spec = document.getElementById("manage-spec-" + id);
        var size = document.getElementById("size-" + id);
        var location = document.getElementById("location-" + id);

        var manage_spec_data = manage_spec.innerHTML;
        //var location_data = location.innerHTML;
        var size_data = size.innerHTML;

        manage_spec.innerHTML = "<input type='text' id='manage-spec-input-" + id + "' value='" + manage_spec_data + "'>";
        // location.innerHTML = "<input type='text' id='loaction-input-" + id + "' value='" + location_data + "'>";
        size.innerHTML = "<input type='number' id='size-input-" + id + "' value='" + size_data + "'>";

    }
    document.getElementById("edit-button-" + id).style.display = "none";
    document.getElementById("save-button-" + id).style.display = "block";
}

function td_click_save(type, id) {

    if (type == "asset")
        var updated = get_corrected_asset(id);
    else if (type == "server")
        var updated = get_corrected_server(id);
    else if (type == "storage")
        var updated = get_corrected_storage(id);
    else if (type == "rack")
        var updated = get_corrected_rack(id);
    else if (type == "switch")
        var updated = get_corrected_switch(id);


    $.ajaxSetup({
        headers: {"X-CSRFToken": getCookie("csrftoken")}
    });

    $.ajax({
        url: '/dbApp/' + type + '/save/' + id + "/",
        type: 'POST',
        data: updated,
        success: function (result) {
            alert("저장되었습니다. 페이지를 새로고침합니다.");
            location.href = "/dbApp/" + type + "/"
        },
        fail: function (result) {
            alert("fail");
        }
    });

}
function get_corrected_storage(id) {
    var manage_spec = document.getElementById("manage-spec-input-" + id);
    var location = document.getElementById("location-input-" + id);
    var standard = document.getElementById("standard-input-" + id);

    var corrected_storage = {
        'manageSpec': manage_spec.value,
        'location': location.value,
        'standard': standard.value
    };
    return corrected_storage;
}

function get_corrected_rack(id) {
    var manage_spec = document.getElementById("manage-spec-input-" + id);
    //var location = document.getElementById("location-input-" + id);
    var size = document.getElementById("size-input-" + id);

    var corrected_rack = {
        'manageSpec': manage_spec.value,
        //  'location': location.value,
        'size': size.value
    };
    return corrected_rack;
}
function get_corrected_switch(id) {
    var manage_spec = document.getElementById("manage-spec-input-" + id);
    var ip = document.getElementById("ip-input-" + id);
    var onoff = document.getElementById("onoff-input-" + id);
    var size = document.getElementById("size-input-" + id);

    var corrected_switch = {
        'manageSpec': manage_spec.value,
        'ip': ip.value,
        'serviceOn': onoff.value,
        'size': size.value
    };
    return corrected_switch;
}
function get_corrected_server(id) {
    var manage_spec = document.getElementById("manage-spec-input-" + id);
    var core = document.getElementById("core-input-" + id);
    var ip = document.getElementById("ip-input-" + id);
    var onoff = document.getElementById("onoff-input-" + id);
    var size = document.getElementById("size-input-" + id);

    var corrected_server = {
        'manageSpec': manage_spec.value,
        'core': core.value,
        'ip': ip.value,
        'onoff': onoff.value,
        'size': size.value
    };
    return corrected_server;
}
function get_corrected_asset(assetNum) {
    var acq_date = document.getElementById("acq-date-input-" + assetNum);
    var name = document.getElementById("name-input-" + assetNum);
    var standard = document.getElementById("standard-input-" + assetNum);
    var acq_cost = document.getElementById("acq-cost-input-" + assetNum);
    var purchase = document.getElementById("purchase-input-" + assetNum);
    var maintenance = document.getElementById("maintenance-input-" + assetNum);

    var target_asset = {
        'acquisitionDate': acq_date.value,
        'assetName': name.value,
        'standard': standard.value,
        'acquisitionCost': acq_cost.value,
        'purchaseLocation': purchase.value,
        'maintenanceYear': maintenance.value
    };

    return target_asset;
}


// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function () {
    $('[data-toggle="modal"]').click(function (e) {
        e.preventDefault();
        var url = $(this).attr('href');
        if (url.indexOf('#') == 0) {
            $(url).modal('open');
        } else {
            $.get(url, function (data) {
                $('<div class="modal fade"><div class="modal-dialog" style="width:70%;text-align: center"><div class="modal-content">' + data + '</div></div></div>')
                    .modal()
                    .on('hidden', function () {
                        $(data_target).remove();
                    });
            }).success(function () {
                $('input:text:visible:first').focus();
            });
        }
    });
});
