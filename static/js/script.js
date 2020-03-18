var log_count = 1;

function get_sides_settings(){
	let value = document.getElementById('sides').checked;
	return value;
}


function log_info(text){
	let box = document.getElementById('info-box');
	box.innerHTML = '<span>'+ log_count + '. </span>' + text + '<br>' + box.innerHTML;
	log_count ++;
}


function uploadFile(file) {
  var url = '/upload'
  var xhr = new XMLHttpRequest()
  var formData = new FormData()
  xhr.open('POST', url + '?double-sided=' + get_sides_settings(), true)

  xhr.addEventListener('readystatechange', function(e) {
	if (this.readyState == 4){
		let body = this.responseText;
		if(this.status == 200) {
	  		log_info('<span class="h4 rounded border">' + body + '</span>');
		}
		else{
			log_info('<span class="h4 rounded bg-danger">ERROR ' + this.status + ":" + body + '</span>');
		}
	}
  })

  formData.append('file', file)
  xhr.send(formData)
}


function dropHandler(ev) {
  console.log('File(s) dropped');

  // Prevent default behavior (Prevent file from being opened)
  ev.preventDefault();

  if (ev.dataTransfer.items) {
	// Use DataTransferItemList interface to access the file(s)
	for (var i = 0; i < ev.dataTransfer.items.length; i++) {
	  // If dropped items aren't files, reject them
	  if (ev.dataTransfer.items[i].kind === 'file') {
		var file = ev.dataTransfer.items[i].getAsFile();
		uploadFile(file);
		console.log('... file[' + i + '].name = ' + file.name);
	  }
	}
  } else {
	// Use DataTransfer interface to access the file(s)
	for (var i = 0; i < ev.dataTransfer.files.length; i++) {
	  console.log('... file[' + i + '].name = ' + ev.dataTransfer.files[i].name);
	}
  }
  this.setAttribute('drop-active', false);
}

function dragOverHandler(ev) {
  console.log('File(s) in drop zone'); 

	// Prevent default behavior (Prevent file from being opened)
	ev.preventDefault();
	this.setAttribute('drop-active', true);
}

function dragLeaveHandler(ev) {
	console.log('drag leave');
	this.setAttribute('drop-active', false);
}