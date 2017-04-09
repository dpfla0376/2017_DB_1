/**
 * Created by 상원 on 2017-04-08.
 * haha
 */
function changeTrColor(tdObj, oldColor, newColor) {
    tdObj.style.backgroundColor = newColor;
    tdObj.onmouseout = function(){
        tdObj.style.backgroundColor = oldColor;
    }
}
function td_click_detail_server(tdObj) {
    var txt = tdObj.text;
    location.href="/dbApp/server/server_detail/?data="+txt;
}
function td_click_detail_rack(tdObj) {
    var txt = tdObj.text;
    location.href="/dbApp/rack/rack_detail/?data="+txt;
}
function td_click_detail_asset(tdObj) {
    var txt = tdObj.text;
    location.href="/dbApp/asset/asset_detail/?data="+txt;
}
function td_click_detail_switch(tdObj) {
    var txt = tdObj.text;
    location.href="/dbApp/switch/switch_detail/?data="+txt;
}

function td_click_delete_asset(assetNum) {
    location.href="/dbApp/asset/delete_asset/?data="+assetNum;
}

function td_click_edit_asset(assetNum) {
    location.href="/dbApp/asset/edit_asset/?data="+assetNum;
}