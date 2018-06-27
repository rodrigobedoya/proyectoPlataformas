$(function(){
    var url = "http://127.0.0.1:5000/shows";

    $("#grid").dxDataGrid({
        dataSource: DevExpress.data.AspNet.createStore({
            key: "id",
            loadUrl: url ,
            insertUrl: url ,
            updateUrl: url ,
            deleteUrl: url ,
            onBeforeSend: function(method, ajaxOptions) {
                ajaxOptions.xhrFields = { withCredentials: true };
            }
        }),
        editing: {
            allowUpdating: true,
            allowDeleting: true,
            allowAdding: true
        },
        remoteOperations: {
            sorting: true,
            paging: true
        },
        paging: {
            pageSize: 12
        },
        pager: {
            showPageSizeSelector: true,
            allowedPageSizes: [8, 12, 20]
        },
        columns: [{
            dataField: "id",
            dataType: "number",
            allowEditing: false
        }, {
            dataField: "name"
        }, {
            dataField: "imageurl"
        }, {
            dataField: "description"
        },{
            dataField: "seasons"
        },{
            dataField: "episodes"
        },{
            dataField: "votes",
            allowEditing:false
        },{
            dataField: "rating",
            allowEditing: false
        },{
            dataField: "rank",
            allowEditing: false
        },],
    }).dxDataGrid("instance");
});