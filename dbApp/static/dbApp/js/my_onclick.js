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
    href = "/dbApp/asset/edit/?data=" + assetNum;
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
/*
 $(document).on('hidden.bs.modal', function (e) {
 $(e.target).remove();

 });*/