// Controle de telas
const loginPage = document.getElementById("page-login");
const cadastroPage = document.getElementById("page-cadastro");
const dashboardPage = document.getElementById("page-dashboard");

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

// Navegação no dashboard
const sections = {
    agenda: document.getElementById("section-agenda"),
    clientes: document.getElementById("section-clientes"),
    configuracoes: document.getElementById("section-configuracoes"),
};
document.querySelectorAll("aside button[data-section]").forEach((btn) => {
    btn.addEventListener("click", () => {
        Object.values(sections).forEach((sec) => sec.classList.add("hidden"));
        const section = btn.getAttribute("data-section");
        sections[section].classList.remove("hidden");
        // Destacar botão ativo
        document
            .querySelectorAll("aside button")
            .forEach((b) => b.classList.remove("bg-gray-200"));
        btn.classList.add("bg-gray-200");
    });
});

// Login simulados
document.getElementById("login-form").addEventListener("submit", (e) => {
    e.preventDefault();
    // Aqui você faria autenticação
    // Para testar, apenas troca para dashboard
    document.getElementById("nome-profissional").textContent =
        document.getElementById("login-email").value;
    loginPage.classList.add("hidden");
    dashboardPage.classList.remove("hidden");
    // Mostrar a agenda por padrão
    Object.values(sections).forEach((sec) => sec.classList.add("hidden"));
    sections["agenda"].classList.remove("hidden");
});

// Cadastro
document
    .getElementById("cadastro-form")
    .addEventListener("submit", (e) => {
        e.preventDefault();
        alert("Conta criada! Faça login.");
        // Voltar ao login
        cadastroPage.classList.add("hidden");
        loginPage.classList.remove("hidden");
    });

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