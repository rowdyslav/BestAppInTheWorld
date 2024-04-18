function displayEditDish(old_title, title, cost, structure) {
	var editDialog = document.getElementsByClassName("edit_dish_dialog")[0];
	editDialog.style.display = "block";
	document.getElementsByClassName("mute")[0].style.display = "block";

	document.getElementById("dishOldTitle").value = old_title;
	document.getElementById("dishEditTitle").value = title;
	document.getElementById("dishEditCost").value = cost;
	document.getElementById("dishEditStructure").value = structure;
}

function closeEdit() {
	var editDialog = document.getElementsByClassName("edit_dish_dialog")[0];
	editDialog.style.display = "none";
	document.getElementsByClassName("mute")[0].style.display = "none";
}
