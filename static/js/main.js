const btnEliminar = document.querySelectorAll('.btn-Eliminar')

if (btnEliminar){
    const btnArray = Array.from(btnEliminar);
    btnArray.forEach((btn) =>{
        btn.addEventListener('click', (e) => {
            if(!confirm("¿Estas Seguro de Eliminar al Usuario?")){
                e.preventDefault();
            }
        });
    });
}