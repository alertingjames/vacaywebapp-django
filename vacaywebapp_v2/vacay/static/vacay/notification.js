var me_email = document.getElementById("me_email").value;
var ul = document.getElementById("list");
var keys = [];
me_email = me_email.replace(".com","").replace(".","ddoott");
var starCountRef = firebase.database().ref('notification/' + me_email);
starCountRef.on('child_added', function(snapshot) {
  var key = snapshot.val();
  if (key){
    var key2 = getChildObj(key);
    var sender_name = key2.senderName
//    window.alert(key2.message);
    var li = document.createElement("div");
    li.style.color = 'black';
    li.style.fontSize = '16';
    li.style.maxWidth = "auto";
    li.style.width = "auto";
    li.innerHTML = sender_name + "<br>" + key2.msg + "<br>" + "<label style='color:red; width:95%; text-align:right; font-size:13px; font-weight:300;'>Click here</label>";
    li.style.textAlign = 'left';
    var ul2 = document.createElement("div");
    var img = document.createElement("img");
    img.src = key2.senderPhoto;
    ul2.appendChild(img);
    ul2.append(li);
    ul2.addEventListener('click', function (event) {
       var context = {
            'friend_email': key2.sender,
            'friend_name': key2.senderName,
            'friend_photo': key2.senderPhoto
       }
       post('/chat_page', context);
    });
    ul.appendChild(ul2);
  }else {
      var lii = document.createElement("div");
      lii.style.color = 'white';
      lii.style.fontSize = '16';
      lii.style.textAlign = 'center';
      lii.innerHTML = "No message ...";
      ul.append(lii);
  }
});

function getChildObj (obj) {
    var obj2;
    for (var p in obj) {
        if (obj.hasOwnProperty(p)) {
            obj2 = obj[p];
        }
    }
    return obj2;
}

function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
       if(params.hasOwnProperty(key)) {
           var hiddenField = document.createElement("input");
           hiddenField.setAttribute("type", "hidden");
           hiddenField.setAttribute("name", key);
           hiddenField.setAttribute("value", params[key]);

              form.appendChild(hiddenField);
       }
    }

    document.body.appendChild(form);
    form.submit();
}












