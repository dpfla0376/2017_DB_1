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
    myConfirm("delete?", function () {
        deleteRequest("/dbApp/asset/delete/", assetNum, "asset-id-");
    });
}

function td_click_delete_server(manageNum) {
    myConfirm("delete?", function () {
        deleteRequest("/dbApp/server/delete/", manageNum, "one-asset-id-");
    });
}

function td_click_delete_storage(manageNum) {
    myConfirm("delete?", function () {
        deleteRequest("/dbApp/storage/delete/", manageNum, "one-asset-id-");
    });
}

function td_click_delete_rack(manageNum) {
    myConfirm("delete?", function () {
        deleteRequest("/dbApp/rack/delete/", manageNum, "one-asset-id-");
    });
}

function td_click_delete_switch(assetNum) {
    myConfirm("delete?", function () {
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
    location.href = "/dbApp/asset/edit/?data=" + assetNum;
}