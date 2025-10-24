var fontSize = 100;
jQuery(document).ready(function(){
		//alert("ok");
			if(_getCookie("fontSize") != null){
				var fontSize = _getCookie("fontSize");
			}else{
				var fontSize = 100;
			}
			jQuery("#fontSize").css("font-size",fontSize + "%");
});
function _getCookie (name) {
	var arg = name + "=";
	var alen = arg.length;
	var clen = document.cookie.length;
	var i = 0;
	while (i < clen) {
		var j = i + alen;
		if (document.cookie.substring(i, j) == arg) {
			return _getCookieVal (j);
		}
		i = document.cookie.indexOf(" ", i) + 1;
		if (i == 0) 
			break;
	}
	return null;
}
function _deleteCookie (name,path,domain) {
	if (_getCookie(name)) {
		document.cookie = name + "=" +
		((path) ? "; path=" + path : "") +
		((domain) ? "; domain=" + domain : "") +
		"; expires=Thu, 01-Jan-70 00:00:01 GMT";
	}
}
function _setCookie (name,value,expires,path,domain,secure) {
	var vurl = true;
	if(path != '' && path != undefined){
		vurl = validUrl(path);
	}
	if(jQuery.type(name) == "string" &&  vurl){
		document.cookie = name + "=" + escape (value) +
		((expires) ? "; expires=" + expires.toGMTString() : "") +
		((path) ? "; path=" + path : "") +
		((domain) ? "; domain=" + domain : "") +
		((secure) ? "; secure" : "");
	}
}
function _getCookieVal (offset) {
	var endstr = document.cookie.indexOf (";", offset);
	if (endstr == -1) { endstr = document.cookie.length; }
	return unescape(document.cookie.substring(offset, endstr));
}
/*********Font size resize**********/
function set_font_size(fontType){
	if(fontType == "increase"){
			 if(fontSize < 130){
			  fontSize = parseInt(fontSize) + 15;
			 }
		  }else if(fontType == "decrease"){
			  if(fontSize > 70){
				fontSize = parseInt(fontSize) - 15;
			  }
		  }else{
			  fontSize = 100;
		  }
	_setCookie("fontSize",fontSize);
	jQuery("#fontSize").css("font-size",fontSize + "%");
	//jQuery("#template_three_column").css("font-size",fontSize + "%");
} 
;

// date 24-2-2016   code for add class in mega menu  written by waliullah 
/*
( function($) {
$(document).ready(function(){
	//alert('hello');
if($('.nav-menu li ul[class="sub-nav-group"] li ul[class="sub-nav-group"] li').find('li')){
 alert('hello');	
}
			
});

} ) ( jQuery );
*/
// code end
jQuery(document).ready(function(){
	jQuery("#edit-search-block-form--2").attr("placeholder", "Search - Keyword, Phrase");
	jQuery(".gtranslate select").attr("id","gtranslate");			   
	jQuery("#gtranslate").before('<label class="notdisplay" for="gtranslate">Google Translate</label>');
	//contrast
	if(getCookie('contrast') == 0 || getCookie('contrast') == null){
	jQuery(".light").hide();
	jQuery(".dark").show();
    }else{
	jQuery(".light").show();
	jQuery(".dark").hide();
	
    }
    jQuery(".search-drop").css("display", "none");
    jQuery(".common-right ul li ul").css("visibility", "hidden");

// Fix Header

	var num = 36; //number of pixels before modifying styles
    jQuery(window).bind('scroll', function () {
        if (jQuery(window).scrollTop() > num) {
        jQuery('.fixed-wrapper').addClass('sticky');
		
    
        } else {
        jQuery('.fixed-wrapper').removeClass('sticky');
    
        }
    });		
			
		
	
// Mobile Nav	
jQuery('.sub-menu').append('<i class="fa fa-caret-right"></i>');
	jQuery('.toggle-nav-bar').click(function(){	
	jQuery('#nav').slideToggle();
	//jQuery('#nav li').removeClass('open');
    
	/*jQuery("#nav li").click(function(){
		jQuery("#nav li").removeClass('open');
		jQuery(this).addClass('open');
	}); */
	
		jQuery("#nav li").hover(
		function() {
		jQuery( this  ).addClass( "open" );
		}, function() {
		jQuery( this ).removeClass( "open" );
		}
		);
		
	});


//Skip Content
jQuery('a[href^="#skipCont"]').click(function() {
jQuery('html,body').animate({ scrollTop: jQuery(this.hash).offset().top}, 500);
//return false;
//e.preventDefault();

});

// Toggle Search



    jQuery("#toggleSearch").click(function(e) {
        jQuery(".search-drop").toggle();
        e.stopPropagation();
		jQuery("#search_key").focus();
    });

    jQuery(document).click(function(e) {
        if (!jQuery(e.target).is('.search-drop, .search-drop *')) {
            jQuery(".search-drop").hide();
        }
    });
	jQuery(".high-contrast.light").click(function (e){
		jQuery(".high-contrast.dark").focus();
		//alert("dark");
		
	});
	jQuery(".high-contrast.dark").click(function (e){
		jQuery(".high-contrast.light").focus();
		//alert("light");
	});


});


jQuery(document).ready(function(){
	
	jQuery("#main-menu div > ul" ).attr("id","nav");

	dropdown1('nav','hover',10);

	dropdown1("header-nav", "hover", 20);

});


jQuery(document).ready(function(){
	
	jQuery('.lang_select').change(function() {
          var url = jQuery(this).val(); // get selected value
          if (url) { // require a URL
              window.location = url; // redirect
          }
          return false;
      });
	

});


//Drop down menu for Keyboard accessing

function dropdown1(dropdownId, hoverClass, mouseOffDelay) { 
	if(dropdown = document.getElementById(dropdownId)) {
		var listItems = dropdown.getElementsByTagName('li');
		for(var i = 0; i < listItems.length; i++) {
			listItems[i].onmouseover = function() { this.className = addClass(this); }
			listItems[i].onmouseout = function() {
				var that = this;
				setTimeout(function() { that.className = removeClass(that); }, mouseOffDelay);
				this.className = that.className;
			}
			var anchor = listItems[i].getElementsByTagName('a');
			anchor = anchor[0];
			anchor.onfocus = function() { tabOn(this.parentNode); }
			anchor.onblur = function() { tabOff(this.parentNode); }
		}
	}
	
	function tabOn(li) {
		if(li.nodeName == 'LI') {
			li.className = addClass(li);
			tabOn(li.parentNode.parentNode);
		}
	}
	
	function tabOff(li) {
		if(li.nodeName == 'LI') {
			li.className = removeClass(li);
			tabOff(li.parentNode.parentNode);
		}
	}
	
	function addClass(li) { return li.className + ' ' + hoverClass; }
	function removeClass(li) { return li.className.replace(hoverClass, ""); }
}

//<![CDATA[
jQuery(function ()
{
jQuery('table').wrap('<div class="scroll-table1"></div>');
jQuery(".scroll-table1").before( "<div class='guide-text'>Swipe to view <i class='fa fa-long-arrow-right'></i></div>" );

});
//]]>


jQuery(document).ready(function(){
	var params = new Array();
	var count = 0;
	jQuery('table.views-table thead tr th').each(function () {
		params[count] = jQuery(this).text();
		count++;	
	});
	jQuery('table.views-table tbody tr').each(function () {
		for(var j = 1; j <= count; j++){
			jQuery('td:nth-child('+j+')', this).attr("data-label",params[j-1]);
		}
	});
});


function burstCache() {
var url = window.location.href;
if(base_url != url && base_url+"/" != url){
if (!navigator.onLine) {
document.body.innerHTML = "Loading...";
window.location = "/";
}
}
}
window.onload = burstCache;






;
//Style Sheet Switcher version 1.1 Oct 10th, 2006

//Author: Dynamic Drive: http://www.dynamicdrive.com
//Usage terms: http://www.dynamicdrive.com/notice.htm

//Unofficial Update to fix Safari 5.1 glitch re: alternate stylesheets or the disabled property in regards to them
// See: http://www.dynamicdrive.com/forums/showthread.php?p=259199 for more info

var manual_or_random="manual" //"manual" or "random"
var randomsetting="3 days" //"eachtime", "sessiononly", or "x days (replace x with desired integer)". Only applicable if mode is random.

//////No need to edit beyond here//////////////

function getCookie(Name) { 
	var re=new RegExp(Name+"=[^;]+", "i"); //construct RE to search for target name/value pair
	if (document.cookie.match(re)) //if cookie found
		return document.cookie.match(re)[0].split("=")[1] //return its value
	return null
}

function setCookie(name, value, days) {
	var expireDate = new Date()
	//set "expstring" to either future or past date, to set or delete cookie, respectively
	var expstring=(typeof days!="undefined")? expireDate.setDate(expireDate.getDate()+parseInt(days)) : expireDate.setDate(expireDate.getDate()-5)
	document.cookie = name+"="+value+"; expires="+expireDate.toGMTString()+"; path=/";
}
 
function deleteCookie(name){
	setCookie(name, "moot")
}

function setStylesheet(title, randomize){ //Main stylesheet switcher function. Second parameter if defined causes a random alternate stylesheet (including none) to be enabled
	var i, cacheobj, altsheets=[""];
	if(setStylesheet.chosen)
	try{
		document.getElementsByTagName('head')[0].removeChild(setStylesheet.chosen);
	}catch(e){}
	for(i=0; (cacheobj=document.getElementsByTagName("link")[i]); i++) {
		if(cacheobj.getAttribute("rel").toLowerCase()=="alternate stylesheet" && cacheobj.getAttribute("title")) { //if this is an alternate stylesheet with title
		cacheobj.disabled = true
		altsheets.push(cacheobj) //store reference to alt stylesheets inside array
			if(cacheobj.getAttribute("title") == title){ //enable alternate stylesheet with title that matches parameter
				cacheobj.disabled = false //enable chosen style sheet
				setStylesheet.chosen = document.createElement('link');//cloneNode(false);
				setStylesheet.chosen.rel = 'stylesheet';
				setStylesheet.chosen.type = 'text/css';
				if(cacheobj.media)
					setStylesheet.chosen.media = cacheobj.media;
				setStylesheet.chosen.href = cacheobj.href;
				document.getElementsByTagName('head')[0].appendChild(setStylesheet.chosen);
			}
		}
	}
	if (typeof randomize!="undefined"){ //if second paramter is defined, randomly enable an alt style sheet (includes non)
		var randomnumber=Math.floor(Math.random()*altsheets.length)
		altsheets[randomnumber].disabled=false
	}
	return (typeof randomize!="undefined" && altsheets[randomnumber]!="")? altsheets[randomnumber].getAttribute("title") : "" //if in "random" mode, return "title" of randomly enabled alt stylesheet
}

function chooseStyle(styletitle, days){ //Interface function to switch style sheets plus save "title" attr of selected stylesheet to cookie
	if (document.getElementById){
		setStylesheet(styletitle)
		setCookie("mysheet", styletitle, days)
	}
}

function indicateSelected(element){ //Optional function that shows which style sheet is currently selected within group of radio buttons or select menu
	if (selectedtitle!=null && (element.type==undefined || element.type=="select-one")){ //if element is a radio button or select menu
		var element=(element.type=="select-one") ? element.options : element
		for (var i=0; i<element.length; i++){
			if (element[i].value==selectedtitle){ //if match found between form element value and cookie value
				if (element[i].tagName=="OPTION") //if this is a select menu
					element[i].selected=true
				else{ //else if it's a radio button
					element[i].checked=true
				}
			break
			}
		}
	}
}
if (manual_or_random=="manual"){ //IF MANUAL MODE
	var selectedtitle=getCookie("mysheet")
	if (document.getElementById && selectedtitle!=null) //load user chosen style sheet from cookie if there is one stored
		setStylesheet(selectedtitle)
}else if (manual_or_random=="random"){ //IF AUTO RANDOM MODE
	if (randomsetting=="eachtime")
		setStylesheet("", "random")
	else if (randomsetting=="sessiononly"){ //if "sessiononly" setting
		if (getCookie("mysheet_s")==null) //if "mysheet_s" session cookie is empty
			document.cookie="mysheet_s="+setStylesheet("", "random")+"; path=/" //activate random alt stylesheet while remembering its "title" value
		else
			setStylesheet(getCookie("mysheet_s")) //just activate random alt stylesheet stored in cookie
	}
	else if (randomsetting.search(/^[1-9]+ days/i)!=-1){ //if "x days" setting
		if (getCookie("mysheet_r")==null || parseInt(getCookie("mysheet_r_days"))!=parseInt(randomsetting)){ //if "mysheet_r" cookie is empty or admin has changed number of days to persist in "x days" variable
			setCookie("mysheet_r", setStylesheet("", "random"), parseInt(randomsetting)) //activate random alt stylesheet while remembering its "title" value
			setCookie("mysheet_r_days", randomsetting, parseInt(randomsetting)) //Also remember the number of days to persist per the "x days" variable
		}
		else
		setStylesheet(getCookie("mysheet_r")) //just activate random alt stylesheet stored in cookie
	} 
}

jQuery(document).ready(function(){		
	jQuery('#menu-item-278 > a, #menu-item-194 > a, #menu-item-192 >  a').click(function(){return false;});		
	jQuery('.dark').click(function(){	
		var thirtyDays = 1000*60*60*24*30;
		var expireDate = new Date((new Date()).valueOf() + thirtyDays);		
		document.cookie = 'contrast' +"="+ 1 +"; expires="+expireDate.toGMTString()+"; path=/";
		document.cookie="username=John Doe";
		jQuery(".light").show();
		jQuery(".dark").hide();
		jQuery(".high-contrast.light").focus();
		jQuery('head').append('<link rel="stylesheet" type="text/css" media="screen" href="'+ base_url +'/'+ modulePath +'/assets/css/change.css">');
		jQuery('head').append('<link rel="stylesheet" type="text/css" media="screen" href="'+ base_url +'/'+ themePath +'/css/site-change.css">');
		jQuery(".national_emblem").attr("src",base_url+"/"+modulePath+"/assets/images/emblem-light.png");// high contrast
		
		jQuery(".ico-skip img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-skip-y.png");
		jQuery(".ico-skip img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-skip-light.png");
		
		//jQuery(".ico-social img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-social-y.png");
		//jQuery(".ico-social img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-social-light.png");
		
		jQuery(".ico-site-search img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-site-search-y.png");
		jQuery(".ico-site-search img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-site-search-light.png");
		
		jQuery(".ico-sitemap img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-sitemap-y.png");
		jQuery(".ico-sitemap img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-sitemap-light.png");
		
		jQuery(".ico-accessibility img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-accessibility-light.png");
		jQuery(".ico-accessibility img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-accessibility-light.png");
		
		jQuery(".sw-logo img").attr("src",base_url+"/"+modulePath+"/assets/images/swach-bharat-y.png");
		
	});
	jQuery('.light').click(function(){	
		var thirtyDays = 1000*60*60*24*30;
		var expireDate = new Date((new Date()).valueOf() + thirtyDays);		
		document.cookie = 'contrast' +"="+ 0 +"; expires="+expireDate.toGMTString()+"; path=/";		
		jQuery(".light").hide();
		jQuery(".dark").show();		
		jQuery(".high-contrast.dark").focus();
		jQuery("[href*='change.css']").remove();
		jQuery(".national_emblem").attr("src",base_url+"/"+modulePath+"/assets/images/emblem-dark.png"); //normal
		
		jQuery(".ico-skip img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-skip.png");
		jQuery(".ico-skip img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-skip-light.png");
		
		//jQuery(".ico-social img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-social.png");
		//jQuery(".ico-social img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-social-light.png");
		
		jQuery(".ico-site-search img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-site-search.png");
		jQuery(".ico-site-search img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-site-search-light.png");
		
		jQuery(".ico-sitemap img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-sitemap.png");
		jQuery(".ico-sitemap img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-sitemap-light.png");
		
		jQuery(".ico-accessibility img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-accessibility.png");
		jQuery(".ico-accessibility img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-accessibility-light.png");
		
		jQuery(".sw-logo img").attr("src",base_url+"/"+modulePath+"/assets/images/swach-bharat.png");

	});
	if(getCookie('contrast') == "1") {
		jQuery('head').append('<link rel="stylesheet" type="text/css" media="screen" href="'+ base_url +'/'+ modulePath +'/assets/css/change.css">');
		jQuery('head').append('<link rel="stylesheet" type="text/css" media="screen" href="'+ base_url +'/'+ themePath +'/css/site-change.css">');
		jQuery(".national_emblem").attr("src",base_url+"/"+modulePath+"/assets/images/emblem-light.png");// high contrast
		
		jQuery(".ico-skip img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-skip-y.png");
		jQuery(".ico-skip img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-skip-light.png");
		
		//jQuery(".ico-social img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-social-y.png");
		//jQuery(".ico-social img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-social-light.png");
		
		jQuery(".ico-site-search img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-site-search-y.png");
		jQuery(".ico-site-search img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-site-search-light.png");
		
		jQuery(".ico-sitemap img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-sitemap-y.png");
		jQuery(".ico-sitemap img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-sitemap-light.png");
		
		jQuery(".ico-accessibility img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-accessibility-light.png");
		jQuery(".ico-accessibility img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-accessibility-light.png");
		
		jQuery(".sw-logo img").attr("src",base_url+"/"+modulePath+"/assets/images/swach-bharat-y.png");
	}
	if(getCookie('contrast') == "0" ) {
		jQuery("[href*='/css/change.css']").remove();
		jQuery(".national_emblem").attr("src",base_url+"/"+modulePath+"/assets/images/emblem-dark.png"); //normal
		
		jQuery(".ico-skip img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-skip.png");
		jQuery(".ico-skip img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-skip-light.png");
		
		//jQuery(".ico-social img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-social.png");
		//jQuery(".ico-social img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-social-light.png");
		
		jQuery(".ico-site-search img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-site-search.png");
		jQuery(".ico-site-search img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-site-search-light.png");
		
		jQuery(".ico-sitemap img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-sitemap.png");
		jQuery(".ico-sitemap img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-sitemap-light.png");
		
		jQuery(".ico-accessibility img.top").attr("src",base_url+"/"+modulePath+"/assets/images/ico-accessibility.png");
		jQuery(".ico-accessibility img.bottom").attr("src",base_url+"/"+modulePath+"/assets/images/ico-accessibility-light.png");
		
		jQuery(".sw-logo img").attr("src",base_url+"/"+modulePath+"/assets/images/swach-bharat.png");
		
	}
});
;
/*
  @file
  Defines the simple modal behavior
*/
(function ($) {
  Drupal.behaviors.event_popup = {
    attach: function(context, settings) {
	  
	    if ($("#event-popup-container").length == 0) {
        // Add a container to the end of the body tag to hold the dialog
        $('body').append('<div id="event-popup-container" style="display:none;"></div>');
        try {
          // Attempt to invoke the simple dialog
          $( "#event-popup-container").dialog({
            autoOpen: false,
            modal: true,
            close: function(event, ui) {
              // Clear the dialog on close. Not necessary for your average use
              // case, butis useful if you had a video that was playing in the
              // dialog so that it clears when it closes
              $('#event-popup-container').html('');
            }
          });
          var defaultOptions = Drupal.event_popup.explodeOptions(settings.event_popup.defaults);
          $('#event-popup-container').dialog('option', defaultOptions);
        }
        catch (err) {
          // Catch any errors and report
          Drupal.event_popup.log('[error] Event Dialog: ' + err);
        }
	    }
	    // Add support for custom classes if necessary
      var classes = '';
      if (settings.event_popup.classes) {
        classes = ', .' + settings.event_popup.classes;
      }
	    $('a.event-popup' + classes, context).each(function(event) {
        if (!event.metaKey && !$(this).hasClass('simpleEventProcessed')) {
          // Add a class to show that this link has been processed already
          $(this).addClass('simpleEventProcessed');
          $(this).click(function(event) {
            // prevent the navigation
            event.preventDefault();
            // Set up some variables
            var url = $(this).attr('href');
            var title = $(this).attr('title');
            // Use defaults if not provided
            var selector = $(this).attr('name') ? 'event-calendar' : 'event_calendar';
            
            var options =  Drupal.event_popup.explodeOptions('width:auto;height:auto;position:[300,140]');
           
            if (url && title && selector) {
              // Set the custom options of the dialog
              $('#event-popup-container').dialog('option', options);
              
              // Set the title of the dialog
              $('#event-popup-container').dialog('option', 'title', title);
              
              // Add a little loader into the dialog while data is loaded
              $('#event-popup-container').html('<div class="event-popup-ajax-loader"></div>');
              
              // Change the height if it's set to auto
              if (options.height && options.height == 'auto') {
                $('#event-popup-container').dialog('option', 'height', 200);
              }
             
              // Use jQuery .get() to request the target page
              $.get(url, function(data) {
                // Re-apply the height if it's auto to accomodate the new content
                if (options.height && options.height == 'auto') {
					 
                  $('#event-popup-container').dialog('option', 'height', options.height);
                  
                }
                // Some trickery to make sure any inline javascript gets run.
                // Inline javascript gets removed/moved around when passed into
                // $() so you have to create a fake div and add the raw data into
                // it then find what you need and clone it. Fun.
                $('#event-popup-container').html( $( '<div></div>' ).html( data ).find( ':regex(class, .*'+selector+'.*)' ).not('.field').clone() );
                
                // Attach any behaviors to the loaded content
                //Drupal.attachBehaviors($('#event-popup-container'));
                
              });
              // Open the dialog
              $('#event-popup-container').dialog('open');
              // Return false for good measure
              return false;
            }
          });
        }
      });
	    var op = Drupal.settings.event_popup.op;
      if(op) {
        $('table.full tr td, table.mini tr td', context).click(function () {
	    //$('.fc-sun', context).click(function () {
			  var node_type = Drupal.settings.event_popup.content_type;
        node_type = node_type.replace('_', '-');
        var url = Drupal.settings.basePath + 'node/add/' +  node_type;
        var title =  'Create Event';
        // Use defaults if not provided
        var selector = Drupal.settings.event_popup.selector;
        //var options =  Drupal.event_popup.explodeOptions(settings.event_popup.defaults);
        var options =  Drupal.event_popup.explodeOptions('width:auto;height:auto;position:[300,140]');
        if (url && title && selector) {
			    var event_date = $(this).attr('data-date');
			    /* var event_date_sep = event_date.split('-');
			    var year = event_date_sep[0];
			    var month = event_date_sep[1];
			    var day = event_date_sep[2]; */
				  // Set the custom options of the dialog
          $('#event-popup-container').dialog('option', options);
          // Set the title of the dialog
          $('#event-popup-container').dialog('option', 'title', title);
          // Add a little loader into the dialog while data is loaded
          $('#event-popup-container').html('<div class="event-popup-ajax-loader"></div>');
          // Change the height if it's set to auto
          if (options.height && options.height == 'auto') {
            $('#event-popup-container').dialog('option', 'height', 200);
          }
          // Use jQuery .get() to request the target page
				
				$.get(url, {'date':event_date}, function(data) {
					
					 // Re-apply the height if it's auto to accomodate the new content
                if (options.height && options.height == 'auto') {
                  $('#event-popup-container').dialog('option', 'height', options.height);
                }
                // Some trickery to make sure any inline javascript gets run.
                // Inline javascript gets removed/moved around when passed into
                // $() so you have to create a fake div and add the raw data into
                // it then find what you need and clone it. Fun.
                $('#event-popup-container').html( $( '<div></div>' ).html( data ).find( '#' + selector ).clone() );
                // Attach any behaviors to the loaded content
                //Drupal.attachBehaviors($('#event-popup-container'));	 
				});
				 // Open the dialog
              $('#event-popup-container').dialog('open');
              // Return false for good measure
              return false;
			}
      });
      }
    }
		  
  };


// Create a namespace for our simple dialog module
  Drupal.event_popup = {};

  // Convert the options to an object
  Drupal.event_popup.explodeOptions = function (opts) {
    var options = opts.split(';');
    var explodedOptions = {};
    for (var i in options) {
      if (options[i]) {
        // Parse and Clean the option
        var option = Drupal.event_popup.cleanOption(options[i].split(':'));
        explodedOptions[option[0]] = option[1];
      }
    }
    return explodedOptions;
  }

  // Function to clean up the option.
  Drupal.event_popup.cleanOption = function(option) {
    // If it's a position option, we may need to parse an array
    if (option[0] == 'position' && option[1].match(/\[.*,.*\]/)) {
      option[1] = option[1].match(/\[(.*)\]/)[1].split(',');
      // Check if positions need be converted to int
      if (!isNaN(parseInt(option[1][0]))) {
        option[1][0] = parseInt(option[1][0]);
      }
      if (!isNaN(parseInt(option[1][1]))) {
        option[1][1] = parseInt(option[1][1]);
      }
    }
    // Convert text boolean representation to boolean
    if (option[1] === 'true') {
      option[1]= true;
    }
    else if (option[1] === 'false') {
      option[1] = false;
    }
    return option;
  }

  Drupal.event_popup.log = function(msg) {
    if (window.console) {
      window.console.log(msg);
    }

  }
  
})(jQuery);
;
/*
  @file
  Defines the simple modal behavior
*/
(function ($) {
  Drupal.behaviors.validates = {
    attach: function(context, settings) {
      var nodeType = Drupal.settings.event_popup.content_type;
      nodeType = nodeType.replace('_', '-');
      var formId = '#' + nodeType + '-node-form #edit-submit';
      $( formId ).click(function () {
      if ($("#display_error").length == 0) {
      $('#event-calendar-node-form').prepend('<div class="messages error" id = "display_error"><h2 class="element-invisible">Error message</h2><ul id="cl"  style="margin-left: 51px;"></ul></div>');
		   }
		  var eventTitle = $( '#edit-title'), 
		  startDate = $( '#edit-event-calendar-date-und-0-value-datepicker-popup-0' ),
		  endDate = $( '#edit-event-calendar-date-und-0-value2-datepicker-popup-0' ), 
		  showEndDate = $( '#edit-event-calendar-date-und-0-show-todate'),
		  allFields = $( [] ).add( eventTitle ).add( startDate ).add( endDate ),
		  tips = $( '#cl' );
		  var bValid = true;
		  allFields.removeClass( "ui-state-error" );
		  bValid = bValid && checkLength( eventTitle, "Event title", 1 );
                  bValid = bValid && checkStartDateLength( startDate, "Date", 1 );
                  if(showEndDate.attr('checked')) { 
                    bValid = bValid && checkEndDateLength( endDate, "Date", 1 );
		    bValid = bValid && DateCompare( startDate, endDate );
		  }
			if(!bValid) {
			  return false;
			}

      function updateTips( t ) {
	      tips
        .html( '<li>' + t + '</li>' )
        .addClass( "ui-state-highlight" );
        setTimeout(function() {
          tips.removeClass( "ui-state-highlight", 1500 );
        }, 500 );
      }
      function checkLength( o, n, min ) {
        if ( o.val().length < 1 ) {
          o.addClass( "ui-state-error" );
          updateTips( "Please enter event title");
            return false;
        } else {
          return true;
        }
      }

     function checkStartDateLength( o, n, min ) {
        if ( o.val().length < 1 ) {
          o.addClass( "ui-state-error" );
          updateTips( "Please enter start date");
            return false;
        } else {
          return true;
        }
      }
      
     function checkEndDateLength( o, n, min ) {
        if ( o.val().length < 1 ) {
          o.addClass( "ui-state-error" );
          updateTips( "Please enter end date");
            return false;
        } else {
          return true;
        }
      }
     
     function DateCompare(startDate, endDate) {
        var str1 = startDate.val();
        var str2 = endDate.val();
        if (str1.trim() != '' && str2.trim() != '') {
          var yr1 = parseInt(str1.substring(6, 10), 10);
          var dt1 = parseInt(str1.substring(3, 5), 10);
          var mon1 = parseInt(str1.substring(0, 2), 10);
          var yr2 = parseInt(str2.substring(6, 10), 10);
          var dt2 = parseInt(str2.substring(3, 5), 10);
          var mon2 = parseInt(str2.substring(0, 2), 10);
          var startDate1 = new Date(yr1, mon1, dt1);
          var endDate1 = new Date(yr2, mon2, dt2);
          if (startDate1 > endDate1) {
            startDate.addClass( "ui-state-error" );
            endDate.addClass( "ui-state-error" );
            updateTips( "Please enter valid date");
            return false;
        }
      }
        return true;
      }
	  });
    }
  };

})(jQuery);
;
