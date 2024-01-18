var handlersContext = {
	switchAction: document.getElementsByClassName("switch_action")[0],
	changeManagersButton: document.getElementsByClassName("change_managers")[0],
	changeCookerButton: document.getElementsByClassName("change_cooker")[0],
	managersForm: document.getElementsByClassName("managers_form")[0],
	cookerForm: document.getElementsByClassName("cooker_form")[0],
};

handlersContext.switchAction.classList.add("before");

handlersContext.changeManagersButton.addEventListener(
	"click",
	changeManagers.bind(handlersContext)
);
handlersContext.changeCookerButton.addEventListener(
	"click",
	changeCooker.bind(handlersContext)
);

function changeManagers() {
	this.switchAction.classList.remove("before");
	this.changeManagersButton.disabled = true;
	this.changeCookerButton.disabled = false;
	this.changeManagersButton.classList.add("clicked");
	this.changeCookerButton.classList.remove("clicked");
	this.managersForm.classList.add("display");
	this.cookerForm.classList.remove("display");
}

function changeCooker() {
	this.switchAction.classList.remove("before");
	this.changeCookerButton.disabled = true;
	this.changeManagersButton.disabled = false;
	this.changeCookerButton.classList.add("clicked");
	this.changeManagersButton.classList.remove("clicked");
	this.cookerForm.classList.add("display");
	this.managersForm.classList.remove("display");
}

// Вызов функции changeManagers при загрузке страницы
changeManagers.call(handlersContext);
