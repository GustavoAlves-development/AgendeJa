// Controle de telas
const loginPage = document.getElementById("page-login");
const cadastroPage = document.getElementById("page-cadastro");

// Links de navegação
document
    .getElementById("link-cadastrar")
    .addEventListener("click", () => {
        loginPage.classList.add("hidden");
        cadastroPage.classList.remove("hidden");
    });
document
    .getElementById("link-voltar-login")
    .addEventListener("click", () => {
        cadastroPage.classList.add("hidden");
        loginPage.classList.remove("hidden");
    });

function verificarStatus() {
    let cliente = document.getElementById("cliente");
    let profissional = document.getElementById("profissional");

    // Verifica se o botão de profissional está selecionado
    if (profissional.checked) {
        // Obtém a primeira div com a classe 'escondidoProfissonais'
        let section = document.getElementsByClassName("escondidoProfissonais")[0];
        section.classList.remove("hidden");
    } else {
        // Caso o cliente seja selecionado, esconde novamente
        let section = document.getElementsByClassName("escondidoProfissonais")[0];
        section.classList.add("hidden");
    }
}
// Modal agendamento
const modal = document.getElementById("modal-agendamento");
document
    .getElementById("btn-novo-agendamento")
    .addEventListener("click", () => {
        modal.classList.remove("hidden");
    });
document.getElementById("btn-cancelar").addEventListener("click", () => {
    modal.classList.add("hidden");
});
document
    .getElementById("form-agendamento")
    .addEventListener("submit", (e) => {
        e.preventDefault();
        alert("Agendamento salvo!");
        modal.classList.add("hidden");
        // Aqui você pode atualizar a lista de agendamentos
    });