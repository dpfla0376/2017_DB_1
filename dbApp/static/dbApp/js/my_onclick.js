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
function td_click_edit_asset(assetNum) {

    document.getElementById("edit-button-" + assetNum).style.display = "none";
    document.getElementById("save-button-" + assetNum).style.display = "block";

    var acq_date = document.getElementById("acq-date-" + assetNum);
    var name = document.getElementById("name-" + assetNum);
    var standard = document.getElementById("standard-" + assetNum);
    var acq_cost = document.getElementById("acq-cost-" + assetNum);
    var purchase = document.getElementById("purchase-" + assetNum);
    var maintenance = document.getElementById("maintenance-" + assetNum);

    var acq_date_data = acq_date.innerHTML;
    var name_data = name.innerHTML;
    var standard_data = standard.innerHTML;
    var acq_cost_data = acq_cost.innerHTML;
    var purchase_data = purchase.innerHTML;
    var maintenance_data = maintenance.innerHTML;

    acq_date.innerHTML = "<input type='date' id='acq-date-input" + assetNum + "' value='" + acq_date_data + "'>";
    name.innerHTML = "<input type='text' id='name-input" + assetNum + "' value='" + name_data + "'>";
    standard.innerHTML = "<input type='text' id='standard-input" + assetNum + "' value='" + standard_data + "'>";
    acq_cost.innerHTML = "<input type='number' id='acq-cost-input" + assetNum + "' value='" + acq_cost_data + "'>";
    purchase.innerHTML = "<input type='text' id='purchase-input" + assetNum + "' value='" + purchase_data + "'>";
    maintenance.innerHTML = "<input type='number' id='maintenance-input" + assetNum + "' value='" + maintenance_data + "'>";

}

function td_click_save_asset(assetNum) {
    var corrected_asset = get_corrected_asset(assetNum);

    $.ajaxSetup({
        headers: {"X-CSRFToken": getCookie("csrftoken")}
    });

    $.ajax({
        url: '/dbApp/asset/save/' + assetNum,
        type: 'POST',
        data: corrected_asset,
        success: function (result) {
            alert("저장되었습니다. 페이지를 새로고침합니다.");
            location.href = "/dbApp/asset/"
        },
        fail: function (result) {
            alert("fail");
        }
    });

}

function get_corrected_asset(assetNum) {
    var acq_date = document.getElementById("acq-date-input" + assetNum);
    var name = document.getElementById("name-input" + assetNum);
    var standard = document.getElementById("standard-input" + assetNum);
    var acq_cost = document.getElementById("acq-cost-input" + assetNum);
    var purchase = document.getElementById("purchase-input" + assetNum);
    var maintenance = document.getElementById("maintenance-input" + assetNum);

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

function edit_request(url, id, id_name) {
    $.ajax({
        url: url + id,
        success: function (result) {
            alert("success");
        },
        fail: function (error) {
            alert("fail");
        }
    });
}

function reload_request(url, id, id_name) {
    $.ajax({
        url: url + id,
        success: function (result) {
            $("#" + id_name + id).reload();
        },
        fail: function (error) {
            alert("fail");
        }
    });
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