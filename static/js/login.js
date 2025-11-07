// Controle de telas
const loginPage = document.getElementById("page-login");
const cadastroPage = document.getElementById("page-cadastro");

// Links de navegação - com verificação de existência
document.getElementById("link-cadastrar")?.addEventListener("click", () => {
    loginPage?.classList.add("hidden");
    cadastroPage?.classList.remove("hidden");
});

document.getElementById("link-voltar-login")?.addEventListener("click", () => {
    cadastroPage?.classList.add("hidden");
    loginPage?.classList.remove("hidden");
});

// Verificar se os elementos de radio button existem antes de adicionar event listeners
const clienteRadio = document.getElementById("cliente");
const profissionalRadio = document.getElementById("profissional");

if (clienteRadio && profissionalRadio) {
    clienteRadio.addEventListener("change", verificarStatus);
    profissionalRadio.addEventListener("change", verificarStatus);
}

function verificarStatus() {
    let cliente = document.getElementById("cliente");
    let profissional = document.getElementById("profissional");

    // Verifica se os elementos existem
    if (!cliente || !profissional) return;

    // Verifica se o botão de profissional está selecionado
    if (profissional.checked) {
        // Obtém a primeira div com a classe 'escondidoProfissonais'
        let sections = document.getElementsByClassName("escondidoProfissonais");
        if (sections.length > 0) {
            sections[0].classList.remove("hidden");
            // INICIALIZAR O EVENT LISTENER AQUI - quando a seção for mostrada
            inicializarTipoProfissional();
        }
    } else {
        // Caso o cliente seja selecionado, esconde novamente
        let sections = document.getElementsByClassName("escondidoProfissonais");
        if (sections.length > 0) {
            sections[0].classList.add("hidden");
        }
    }
}

// Variável para armazenar a função de evento (para poder remover depois)
let currentTipoChangeHandler = null;

// Função para inicializar o controle do tipo de profissional
function inicializarTipoProfissional() {
    const tipoUsuario = document.getElementById("tipo-profissional");
    const inputTipo = document.getElementById("tipo-outro-input");

    // Só inicializar se os elementos existirem
    if (tipoUsuario && inputTipo) {
        // Remover event listener anterior se existir
        if (currentTipoChangeHandler) {
            tipoUsuario.removeEventListener("change", currentTipoChangeHandler);
        }

        // Criar nova função handler
        currentTipoChangeHandler = function() {
            if (this.value === "Outro") {
                inputTipo.classList.remove("hidden");
            } else {
                inputTipo.classList.add("hidden");
            }
        };

        // Adicionar novo event listener
        tipoUsuario.addEventListener("change", currentTipoChangeHandler);

        // Verificar estado inicial
        currentTipoChangeHandler.call(tipoUsuario);
    }
}

// Código do modal - com verificação de existência
const modal = document.getElementById("modal-agendamento");
document.getElementById("btn-novo-agendamento")?.addEventListener("click", () => {
    modal?.classList.remove("hidden");
});

document.getElementById("btn-cancelar")?.addEventListener("click", () => {
    modal?.classList.add("hidden");
});

document.getElementById("form-agendamento")?.addEventListener("submit", (e) => {
    e.preventDefault();
    alert("Agendamento salvo!");
    modal?.classList.add("hidden");
    // Aqui você pode atualizar a lista de agendamentos
});

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Verificar status inicial (caso a página carregue com algum selecionado)
    verificarStatus();

    // Inicializar tipo profissional se já estiver visível
    const profissionalRadio = document.getElementById("profissional");
    if (profissionalRadio && profissionalRadio.checked) {
        inicializarTipoProfissional();
    }
});

class DropdownManager {
    constructor() {
        this.dropdowns = new Set();
        this.isInitialized = false;
    }

    init() {
        if (this.isInitialized) return;

        document.addEventListener('click', this.handleDocumentClick.bind(this));
        document.addEventListener('keydown', this.handleKeydown.bind(this));
        this.registerExistingDropdowns();

        this.isInitialized = true;
    }

    registerExistingDropdowns() {
        const dropdownContainers = document.querySelectorAll('.user-dropdown-container');
        dropdownContainers.forEach(container => {
            this.registerDropdown(container);
        });
    }

    registerDropdown(container) {
        const toggle = container.querySelector('.dropdown-toggle');
        const menu = container.querySelector('.dropdown-menu');
        const arrow = container.querySelector('.dropdown-arrow');

        if (!toggle || !menu) {
            console.warn('Dropdown elements not found in container:', container);
            return;
        }

        const dropdownData = {
            container,
            toggle,
            menu,
            arrow,
            isOpen: false
        };

        this.dropdowns.add(dropdownData);

        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown(dropdownData);
        });

        // Prevenir que cliques no menu fechem o dropdown
        menu.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }

    toggleDropdown(dropdownData) {
        if (dropdownData.isOpen) {
            this.closeDropdown(dropdownData);
        } else {
            this.openDropdown(dropdownData);
        }
    }

    openDropdown(dropdownData) {
        // Fecha outros dropdowns abertos
        this.closeAllDropdowns();

        dropdownData.menu.classList.remove('hidden');
        dropdownData.menu.classList.add('open');
        dropdownData.menu.classList.remove('closing');

        if (dropdownData.arrow) {
            dropdownData.arrow.classList.add('rotated');
        }

        dropdownData.isOpen = true;

        // Trigger custom event
        this.triggerEvent('dropdownOpened', dropdownData.container);
    }

    closeDropdown(dropdownData) {
        dropdownData.menu.classList.add('closing');
        dropdownData.menu.classList.remove('open');

        if (dropdownData.arrow) {
            dropdownData.arrow.classList.remove('rotated');
        }

        dropdownData.isOpen = false;

        // Espera a animação terminar antes de esconder
        setTimeout(() => {
            if (!dropdownData.isOpen) {
                dropdownData.menu.classList.add('hidden');
                dropdownData.menu.classList.remove('closing');
            }
        }, 200);

        // Trigger custom event
        this.triggerEvent('dropdownClosed', dropdownData.container);
    }

    closeAllDropdowns() {
        this.dropdowns.forEach(dropdownData => {
            if (dropdownData.isOpen) {
                this.closeDropdown(dropdownData);
            }
        });
    }

    handleDocumentClick(e) {
        let clickedInsideDropdown = false;

        this.dropdowns.forEach(dropdownData => {
            if (dropdownData.container.contains(e.target)) {
                clickedInsideDropdown = true;
            }
        });

        if (!clickedInsideDropdown) {
            this.closeAllDropdowns();
        }
    }

    handleKeydown(e) {
        if (e.key === 'Escape') {
            this.closeAllDropdowns();
        }
    }

    triggerEvent(eventName, element, data = null) {
        const event = new CustomEvent(eventName, {
            detail: data,
            bubbles: true
        });
        element.dispatchEvent(event);
    }

    // Método público para fechar todos os dropdowns
    closeAll() {
        this.closeAllDropdowns();
    }

    // Método público para destruir o manager
    destroy() {
        document.removeEventListener('click', this.handleDocumentClick);
        document.removeEventListener('keydown', this.handleKeydown);
        this.dropdowns.clear();
        this.isInitialized = false;
    }
}

// Singleton instance
const dropdownManager = new DropdownManager();

// Auto-inicialização quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        dropdownManager.init();
    });
} else {
    dropdownManager.init();
}

// Export para uso em outros arquivos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = dropdownManager;
} else {
    window.dropdownManager = dropdownManager;
}