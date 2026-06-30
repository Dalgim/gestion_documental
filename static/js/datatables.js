function inicializarTabla(idTabla){

    new DataTable(idTabla,{

        language:{
            url:'https://cdn.datatables.net/plug-ins/2.3.2/i18n/es-MX.json'
        },

        pageLength:10,
        lengthMenu:[
            [10,25,50,100],
            [10,25,50,100]
        ],

        ordering:true,
        responsive:true

    });

}