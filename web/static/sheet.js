senechalConfig = {}

skills = []
passions = []
cid = 32;
var searchParams = new URLSearchParams(window.location.search);
char = {}
data = {}
event = {}

const options = {
mode: 'code',
modes: ['code', 'form', 'text', 'tree', 'view', 'preview']
}
editor = {}

var surl = 'https://senechal.herokuapp.com'
if (window.location.href.indexOf('localhost')>0) {
    surl = '..';
    cid = 63;
}
if (localStorage.getItem('cid')) {
    cid = localStorage.getItem('cid')
}

if (searchParams.has('cid')) {
    cid=searchParams.get('cid')
}

function eventdialog(id) {
    if ('memberId' in char ) {
        event =  {'year': 0, 'description': '', 'glory': 0, 'id': -1}
        if ('events' in data) {
            for (eid in data['events']) {
                if (data['events'][eid]['id'] == id) {
                    event = data['events'][eid];
                }
            }
        }
        $('#eventid').html(id>0?id:'--')
        $('#eventyear').val(event['year'])
        $('#eventglory').val(event['glory'])
        $('#eventdescription').html(event['description'])
        $("#eventdialog" ).dialog('open');
    }
}

function mark(name) {
    $( "#markdialog" ).dialog({
      height: "auto",
      width: 400,
      modal: true,
      buttons: {
        "Bejelölöm": function() {
          $( this ).dialog( "close" );
          $.post( surl+"/mark", {'id':char['memberId'], 'mark':name},function( data ) {
            redraw(data)
            console.log('marked')
          });
        },
        Mégsem: function() {
          $( this ).dialog( "close" );
        }
      }
    });
    $( "#markdialog" ).dialog('open');
}

function redrawMain() {
    if  ('url' in char) {
        $('#charimg').attr('src',char['url'])
        $('#charimg').show()
    } else {
        $('#charimg').hide()
    }

    $('#main').html('')
    if ('main' in char) {
        for (const [n, v] of Object.entries(char['main'])) {
            if (n != 'Glory') {
                $('#main').append('<li><span class="gold">'+n+'</span> '+v+'</li>');
            }
            if (n.toLowerCase() == 'born') {
                $('#main').append('<li><span class="gold">Year</span> '+data['year']+'</li>');
                $('#main').append('<li><span class="gold">Age</span> '+(data['year']*1-v*1)+'</li>');
            }
        }
    }
      $('#description').html('')
      if ('description' in char) {
        $('#description').html(char['description'].replace(/\n/g, "<br/>"))
      }
      $('#longdescription').html('')
      if ('longdescription' in char) {
        $('#longdescription').html(char['longdescription'].replace(/\n/g, "<br/>"))
      }
}

function redrawStat() {
      $('#hp').html('?');
      if ('stats' in char) {
          $('#statistics').html(
          '<li><span class="gold">SIZ</span> '+char['stats']['siz']+'</li>'
          +'<li><span class="gold">DEX</span> '+char['stats']['dex']+'</li>'
          +'<li><span class="gold">STR</span> '+char['stats']['str']+'</li>'
          +'<li><span class="gold">CON</span> '+char['stats']['con']+'</li>'
          +'<li><span class="gold">APP</span> '+char['stats']['app']+'</li>'
          +'<li><span class="gold">Damage</span> <em> (STR+SIZ)/6=</em> <strong>'+Math.round((char['stats']['str']*1+char['stats']['siz']*1)/6)+'d6 </strong></li>'
          +'<li><span class="gold">Healing Rate</span> <em> (STR+CON)/10=</em> <strong>'+Math.round((char['stats']['con']*1+char['stats']['str']*1)/10)+' </strong></li>'
          +'<li><span class="gold">Move Rate</span> <em> (STR+DEX)/10=</em> <strong>'+Math.round((char['stats']['dex']*1+char['stats']['siz']*1)/10)+' </strong></li>'
          +'<li><span class="gold">Total Hitpoints</span> <em> (SIZ+CON)=</em> <strong>'+Math.round((char['stats']['siz']*1+char['stats']['con']*1))+' </strong></li>'
          +'<li><span class="gold">Unconscious</span> <em> (HP/4)=</em> <strong>'+Math.round((char['stats']['con']*1+char['stats']['siz']*1)/4)+' </strong></li>'
          +'<li><span class="gold">Major Wound</span> <em> (CON)=</em> <strong>'+char['stats']['con']+' </strong></li>'
          +'<li><span class="gold">Knockdown</span> <em> (SIZ)=</em> <strong>'+char['stats']['siz']+' </strong></li>'
          );
          hp = (char['stats']['siz']*1+char['stats']['con']*1);
          maxhp = hp;
          s='Changes: '
          if (char['health'] && char['health']['changes']) {
            for(i in  char['health']['changes']) {
                if (i>0) {
                  s+=', '
                }
                s+=char['health']['changes'][i]
                hp += char['health']['changes'][i]
                if (hp>maxhp) {
                    hp = maxhp;
                }
            }
          }
          if (hp>=maxhp) {
              $('#hp').html(maxhp)
              $('#hp').attr('title', 'Healthy')
          } else {
              $('#hp').html(hp+"/"+maxhp)
              $('#hp').attr('title', s)
          }
          $('#chineed').prop('checked', char['health']['chirurgery'])
          $('#hp').tooltip()
      }


}

function redrawEvents() {
      $('#events').html('');
      $('#glory').html('?');
      year = -1;
      if ('events' in data) {
          glory = 0;
          s = ''
          for (eid in data['events']) {
            event = data['events'][eid];
            glory+=event['glory'];

            if (year != event['year']) {
                year = event['year'];
                $('#events').append('<h3>'+event['year']+'</h3> <div id="year_'+year+'"></div>');
            }
            $('#year_'+year).append('<div id="event_'+event['id']+'" class="event">'+(event['glory']>0?'<span class="gold">'+event['glory']+'</span> ':'')+'<span>'+event['description'].replace(/\n/g, "<br/>")+'</span></div>')
          }
          $('#events').accordion('refresh');
          $('#glory').html(glory);
      }

      $('div.event').click(function() {
        eventdialog($(this).attr('id').substr(6));
      })
}

function redrawSkill() {
      $('#combat').html('')
      $('#skills').html('')
      if ('skills' in char) {
          skillcount = 0;
          skills = []
          for (const [sgn, sgv] of Object.entries(char['skills'])) {
              for (const [sn, sv] of Object.entries(sgv)) {
                  $(sgn=='Other'?'#skills':'#combat').append('<li id="skill_'+skillcount+'"><span class="ui-icon ui-icon-radio-off" mark="'+sn+'"></span><span class="gold">'+sn+'</span> '+sv+'</li>');
                  skills[skillcount++]='skills.'+sgn+'.'+sn;
              }
          }
      }
}

function redrawPassion() {
      $('#passions').html('')
      if ('passions' in char) {
          count = 0;
          passions = []
          for (const [pn, pv] of Object.entries(char['passions'])) {
              $('#passions').append('<li id="passion_'+count+'"><span class="ui-icon ui-icon-radio-off" mark="'+pn+'"></span><span class="gold">'+pn+'</span> '+pv+'</li>');
              passions[count++]='passions.'+pn;
          }
      }
}

function redrawTrait() {
      if ('traits' in char) {
         $('#traits').show();
         for (const [tn, tv] of Object.entries(char['traits'])) {
            $('#trait_'+tn+' tr:first-child  td:nth-child(2)').text(tv)
            $('#trait_'+tn+' tr:first-child  td:nth-child(5)').text(20-tv*1)
            $('#trait_'+tn+' .ratioGreen').css('width', (5*tv)+"%")
            $('#trait_'+tn+' .ratioRed').css('width', 5*(20-tv)+"%")
         }
      } else {
       $('#traits').hide();
      }
}

function redrawNpc(npc) {
    id = npc['char']['dbid']
    console.log(id+":"+npc)
    if (npc['char']['description']) {
        console.log(npc['char']['description'])
        $('#npc_'+npc['char']['dbid']).append('<p>'+npc['char']['description']+'</p>')
    }
    if (npc['char']['url']) {
        $('#npc_'+npc['char']['dbid']).append('<img width="100%" src="'+npc['char']['url']+'"/>')
    }
    table = $('#npct_'+id)
    if (npc['char']['main']) {
        for (const [n, v] of Object.entries(npc['char']['main'])) {
            table.append('<tr><th>'+n+'</th><td>'+v+'</td></tr>');
        }
    }
    if (npc['char']['stats']) {
        for (const [n, v] of Object.entries(npc['char']['stats'])) {
            table.append('<tr><th>'+n+'</th><td>'+v+'</td></tr>');
        }
    }
    if (npc['char']['skills']) {
        for (const [n, v] of Object.entries(npc['char']['skills'])) {
            for (const [n2, v2] of Object.entries(v)) {
                table.append('<tr><th>'+n2+'</th><td>'+v2+'</td></tr>');
            }
        }
    }
    if (npc['char']['passions']) {
        for (const [n, v] of Object.entries(npc['char']['passions'])) {
            table.append('<tr><th>'+n+'</th><td>'+v+'</td></tr>');
        }
    }
}

function npc(npc) {
    s='<h5>'+npc['name']+' <i>('+npc['connection']+')</h5>';
    if ('dbid' in npc) {
        s+='<div id="npc_'+npc['dbid']+'"></div>'
        $.get( surl + "/npc?id="+npc['dbid'],function( data ) {
          redrawNpc(data)
        });
    }
    s+='<table class="stats" '+(npc['dbid']?(' id="npct_'+npc['dbid']+'"'):"")+'>'
    if ('show' in npc) {
       for (const [n2, v2] of Object.entries(npc['show'])) {
            s += '<tr><th>'+n2+'</th><td>'+v2+'</td></tr>';
            if (n2.toLowerCase()=='born') {
                s += '<tr><th>Age</th><td>'+(data['year']*1-v2*1)+'</td></tr>';
            }
        }
    }
    if ('skills' in npc) {
       for (const [n2, v2] of Object.entries(npc['skills'])) {
            s += '<tr><th>'+n2+'</th><td>'+v2+'</td></tr>';
        }
    }
    s+='</table>'
    return s
}


function getweapon(spec) {
    w = {}
    for (const [n, v] of Object.entries(senechalConfig['weapons']['default'])) {
        w[n] = v
    }
    if (senechalConfig['weapons'][spec]) {
        for (const [n, v] of Object.entries(senechalConfig['weapons'][spec])) {
             w[n] = v
        }
    }
    return w
}

function redrawAccordion() {
      $('#army').html('')
      if ('army' in char) {
          for (const [n, v] of Object.entries(char['army'])) {
             $('#army').append('<tr><th>'+n+'</th><td>'+v+'</td></tr>');
          }
      }
      $('#accordion .npcs').remove()
      if ('npcs' in char) {
          for (const [n, v] of Object.entries(char['npcs'])) {
             $('#accordion').append('<h3 class="npcs">'+n+'</h3><div class="npcs">'+npc(v)+'</div>');
          }
      }

     horses = char['winter']['horses']
     htype = senechalConfig['horsetypes'][horses[0]];
     $('#htyp').html(horses[0]);
     $('#harm').html(htype['arm'])
     $('#hsiz').html(htype['siz'])
     $('#hdex').html(htype['dex'])
     $('#hstr').html(htype['str'])
     $('#hcon').html(htype['con'])

     $('#hdam').html(htype['dam'])
     $('#hhea').html(Math.round((htype['con']*1+htype['str']*1)/10))
     $('#hmov').html(htype['mov'])
     $('#hhp').html(Math.round((htype['siz']*1+htype['con']*1)))
     $('#hunc').html(Math.round((htype['con']*1+htype['siz']*1)/4))
     $('#hother').html('');
     for(i in horses) {
        if (i>0) {
            mov = '???'
            if (horses[i] in senechalConfig['horsetypes']) {
                htype = senechalConfig['horsetypes'][horses[i]]
                mov = htype['mov']
            }
            $('#hother').append('<tr><th>Type</th><td>'+horses[i]+'</td><th>Move</th><td>'+mov+'</td></tr>')
        }
     }
    $('#accordion').accordion("refresh");

     $('#weapon option[value="'+char['combat']['weapon']+'"]').prop('selected', true)
     $('#armor option[value="'+char['combat']['armor']+'"]').prop('selected', true)
     $('#shield option[value="'+char['combat']['shield']+'"]').prop('selected', true)
     $('#shield, #weapon, #armor').selectmenu( "refresh" );
     w = getweapon(char['combat']['weapon'])
     $('#combatgear').html('')
     $('#combatgear').append('<tr><th>Skill</th><td>'+w['skill']+'</td></tr>')
     $('#combatgear').append('<tr><th>Damage</th><td>'+(Math.round((char['stats']['str']*1+char['stats']['siz']*1)/6)+w.damage)+'d6</td></tr>')

     $('#combatgear').append('<tr><th>Damage reduction</th><td>'
        +senechalConfig['armors'][char['combat']['armor']]['red']
        +' + '
        +senechalConfig['shields'][char['combat']['shield']]['red']
        +'</td></tr>')
     $('#combatgear').append('<tr><th>Dex modifier</th><td>'
        +senechalConfig['armors'][char['combat']['armor']]['dex']
        +'</td></tr>')
     $('#combatgear').append('<tr><th>Effective Dex</th><td>'
        +(char['stats']['dex'] + senechalConfig['armors'][char['combat']['armor']]['dex'])
        +'</td></tr>');

/*
                        <tr><th>Damage reduction</th><td>{{base.armors[char.char['combat']['armor']]['red']}}
                            + {{base.armors[char.char['combat']['shield']]['red']}} </td></tr>
                         <tr><th>Dex modifier</th><td>{{base.armors[char.char['combat']['armor']]['red']}}</td></tr>
                         <tr><th>Effective Dex</th><td>{{char.char['stats']['dex'] + base.armors[char.char['combat']['armor']]['red']}}</td></tr>

*/

}

function redraw(newdata) {
    if (data['modified']  != newdata['modified']) {
        data = newdata;
        char = newdata['char'];
        redrawMain();
        redrawStat();
        redrawSkill();
        redrawPassion();
        redrawTrait();
        redrawAccordion();
        $('[mark]').on('click',function() {
            mark($(this).attr('mark'));
        });
    }
    data = newdata;
    redrawEvents();

     $('.ui-icon-bullet').removeClass('ui-icon-bullet').addClass('ui-icon-radio-off')
     if ('marks' in data) {
         for (i in skills) {
            if (data['marks'].includes(skills[i].replace(/.*\./g, ""))) {
                $('#skill_'+i+' .ui-icon').removeClass('ui-icon-radio-off').addClass('ui-icon-bullet')
            }
         }
         for (i in passions) {
            if (data['marks'].includes(passions[i].replace(/.*\./g, ""))) {
                 $('#passion_'+i+' .ui-icon').removeClass('ui-icon-radio-off').addClass('ui-icon-bullet')
            }
         }
         traits = senechalConfig['traits']
         for (i in traits) {
            if (data['marks'].includes(traits[i][0])) {
              $('#trait_'+traits[i][0].toLowerCase().substring(0,3)+' .left').removeClass('ui-icon-radio-off').addClass('ui-icon-bullet')
            }
            if (data['marks'].includes(traits[i][1])) {
              $('#trait_'+traits[i][0].toLowerCase().substring(0,3)+' .right').removeClass('ui-icon-radio-off').addClass('ui-icon-bullet')
            }
         }
     }
}
function refreshdata(id) {
    if (cid != id) {
        data['modified'] = -1;
    }
    cid = id;
    localStorage.setItem('cid', id)
    $('#pdf').attr('href', surl + '/pdf?id='+id)
    $.get( surl + "/json?id="+id,function( data ) {
      redraw(data)
    });
}

  $( function() {
      $.fn.inputFilter = function(inputFilter) {
        return this.on("input keydown keyup mousedown mouseup select contextmenu drop", function() {
          if (inputFilter(this.value)) {
            this.oldValue = this.value;
            this.oldSelectionStart = this.selectionStart;
            this.oldSelectionEnd = this.selectionEnd;
          } else if (this.hasOwnProperty("oldValue")) {
            this.value = this.oldValue;
            this.setSelectionRange(this.oldSelectionStart, this.oldSelectionEnd);
          } else {
            this.value = "";
          }
        });
      };

    const container = document.getElementById('jsoneditor')
    editor = new JSONEditor(container, options)
    $('#accordion').accordion();
    $('#events').accordion();
    $("button" ).button();
    $(".controlgroup" ).controlgroup()
    $('#wound').click(function( event ) {
        mod = $('#healthmod').val()*1;
        if (mod>0) {
            char['health']['changes'].push(mod*-1)
            if (mod > char['stats']['con']) {
                char['health']['chirurgery'] = 1;
            }
            $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                console.log('modified')
            });
            redrawStat()
        }
        event.preventDefault();
    } )
    $('#heal').click(function( event ) {
        mod = $('#healthmod').val()*1;
        if (mod>0) {
            char['health']['changes'].push(mod)
            $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                console.log('modified')
            });
            redrawStat()
        }
        event.preventDefault();
    } )
    $('#completeheal').click(function( event ) {
        char['health'] = {changes:[],chirurgery:0}
        $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
            console.log('modified')
        });
        redrawStat()
    })
    $('#sunday').click(function( event ) {
        char['health']['changes'].push(Math.round((char['stats']['con']*1+char['stats']['str']*1)/10))
        $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
            console.log('modified')
        });
        redrawStat()
    })
    $("#healthmod").inputFilter(function(value) {
        return /^\d*$/.test(value);    // Allow digits only, using a RegExp
    });
    $('#chineed').change(function(event) {
        console.log( this.checked)
        char['health']['chirurgery']= this.checked ? 1 : 0;
        $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
            console.log('modified')
        });
        redrawStat()
    })
    $.get( surl+"/base",function( base ) {
        senechalConfig = base
        for (const [n, v] of Object.entries(senechalConfig ['weapons'])) {
            if ('default'!=n) {
                $('#weapon').append('<option value="'+n+'">'+n+'</option>')
            }
        }
        for (const [n, v] of Object.entries(senechalConfig ['armors'])) {
            $('#armor').append('<option value="'+n+'">'+n+'</option>')
        }
        for (const [n, v] of Object.entries(senechalConfig ['shields'])) {
            $('#shield').append('<option value="'+n+'">'+n+'</option>')
        }
        $( "#weapon" ).selectmenu({
            change: function( event, data ) {
               char['combat']['weapon'] = data.item.value
               $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                 redraw(data)
               });
            }
          })
        $( "#armor" ).selectmenu({
            change: function( event, data ) {
               char['combat']['armor'] = data.item.value
               $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                 redraw(data)
               });
            }
          })
        $( "#shield" ).selectmenu({
            change: function( event, data ) {
               char['combat']['shield'] = data.item.value
               $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                 redraw(data)
               });
            }
          })
        $.get( surl+"/json",function( list ) {
          for (const [n, v] of Object.entries(list)) {
             $('#character').append('<option value="'+v+'" '+(v==cid?' selected="selected"':"")+'>'+n+'</option>>');
          }
          $( "#character" ).selectmenu({
            change: function( event, data ) {
                console.log(data.item.value)
                refreshdata(data.item.value);
            }
          })
        });
    });

     $('.ui-icon-bullet').hide();
     $('#passions .ui-icon').hide();
     refreshdata(cid);
     setInterval(function (){refreshdata(cid)},60000)
     $( "#markdialog" ).dialog({autoOpen: false});
     $( "#eventdialog" ).dialog({
      autoOpen: false,
      dialogClass: 'ui-widget-shadow',
      height: "auto",
      width: 800,
      modal: true,
      buttons: {
        "Rögzítem": function() {
          $( this ).dialog( "close" );
          $.post( surl+"/event", {
            'eid':event['id']
            , 'glory':$('#eventglory').val()
            , 'year':$('#eventyear').val()
            , 'description':$('#eventdescription').val()
            , 'mid':char['memberId']
            },function( data ) {
            redraw(data)
            console.log('marked')
          });
        },
        "Törlöm": function() {
          $( this ).dialog( "close" );
          $.post( surl+"/event", {'eid':event['id'], 'glory':-1, 'mid':char['memberId']},function( data ) {
            redraw(data)
            console.log('marked')
          });
        },
        "Mégsem": function() {
          $( this ).dialog( "close" );
        }
      }
    });

     $( "#newchardialog" ).dialog({
      autoOpen: false,
      dialogClass: 'ui-widget-shadow',
      height: "auto",
      width: 800,
      modal: true,
      buttons: {
        "Rögzítem": function() {
          $( this ).dialog( "close" );
          $.post( surl+"/newchar", {'json':JSON.stringify({
            'name':$('#newcharname').val()
            , 'url':$('#newcharurl').val()
            , 'description':$('#newchardescription').val()
            })},function( data ) {
                $('#character').append('<option value="'+data['char']['dbid']+'">'+data['char']['name']+'</option>>');
                $("#character").selectmenu( "refresh" );
                redraw(data)
          });
        },
        "Mégsem": function() {
          $( this ).dialog( "close" );
        }
      }
    });

     jsondialog = $( "#jsondialog" ).dialog({
        autoOpen: false,
        dialogClass: 'ui-widget-shadow',
        height: 800,
        width: 800,
        modal: true,
      show: {
        effect: "blind",
        duration: 1000
      },
      hide: {
        effect: "explode",
        duration: 1000
      },
    });
    $('#eventshead').click(function(){
        console.log('eventshead')
        eventdialog(-1);
    })

    $('#newchar').click(function(){
        $("#newchardialog" ).dialog('open');
    })

    $('.skillhead').on( "click", function() {
        $( "#json" ).val(JSON.stringify(char, null, 2))
        editor.set(char['skills'])
        jsondialog.dialog("option", "buttons", [ {
             text: "Modify",
             click: function() {
               jsondialog.dialog( "close" );
               char['skills']= editor.get()
               $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                 console.log('modified')
                 redraw(data)
               });
             }
           } ] )
        jsondialog.dialog( "open" );
    });
    $('#traithead').on( "click", function() {
        $( "#json" ).val(JSON.stringify(char, null, 2))
        editor.set(char['traits'])
        jsondialog.dialog("option", "buttons", [ {
             text: "Modify",
             click: function() {
               jsondialog.dialog( "close" );
               char['traits']= editor.get()
               $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                 console.log('modified')
                 redraw(data)
               });
             }
           } ] )
        jsondialog.dialog( "open" );
    });
    $('#passionhead').on( "click", function() {
        editor.set(char['passions'])
        jsondialog.dialog("option", "buttons", [ {
             text: "Modify",
             click: function() {
               jsondialog.dialog( "close" );
               char['passions']= editor.get()
               $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                 console.log('modified')
                 redraw(data)
               });
             }
           } ] )
        jsondialog.dialog( "open" );
    });
    $('#mainhead').on( "click", function() {
        editor.set(char['main'])
        jsondialog.dialog("option", "buttons", [ {
             text: "Modify",
             click: function() {
               jsondialog.dialog( "close" );
               char['main']= editor.get()
               $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                 console.log('modified')
                 redraw(data)
               });
             }
           } ] )
        jsondialog.dialog( "open" );
    });
    $('#stathead').on( "click", function() {
        editor.set(char['stats'])
        jsondialog.dialog("option", "buttons", [ {
             text: "Modify",
             click: function() {
               jsondialog.dialog( "close" );
               char['stats']= editor.get()
               $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(char)},function( data ) {
                 console.log('modified')
                 redraw(data)
               });
             }
           } ] )
        jsondialog.dialog( "open" );
    });
    $( "#editchar" ).on( "click", function() {
      $( "#json" ).val(JSON.stringify(char, null, 2))
      editor.set(char)
      jsondialog.dialog("option", "buttons", [ {
              text: "Modify",
              click: function() {
                jsondialog.dialog( "close" );
                $.post( surl+"/modify", {'id':cid, 'json':JSON.stringify(editor.get())},function( data ) {
                  console.log('modified')
                  redraw(data)
                });
              }
            } ] )
      jsondialog.dialog( "open" );
    });
    $('.traitcheck').on('click', function() {
        tid = $(this).parent().parent().parent().attr('id').substring(6,9);
        console.log($(this).hasClass('left')+":"+tid);
        for (i in traits) {
           if (traits[i][0].toLowerCase().substring(0,3) == tid ) {
              mark(traits[i][$(this).hasClass('left')?0:1])
           }
        }
    });

    $( document ).tooltip({
      items: "#hp"
    });
  });
