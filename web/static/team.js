traits = [
    [ 'Chaste', 'Lustful' ],
    [ 'Energetic', 'Lazy' ],
    [ 'Forgiving', 'Vengeful' ],
    [ 'Generous', 'Selfish' ],
    [ 'Honest', 'Deceitful' ],
    [ 'Just', 'Arbitrary' ],
    [ 'Merciful', 'Cruel' ],
    [ 'Modest', 'Proud' ],
    [ 'Prudent', 'Reckless' ],
    [ 'Spiritual', 'Worldly' ],
    [ 'Temperate', 'Indulgent' ],
    [ 'Trusting', 'Suspicious' ],
    [ 'Valorous', 'Cowardly' ],
    ];
var surl = 'https://senechal.herokuapp.com'
if (window.location.href.indexOf('localhost')>0) {
    surl = '..';
    cid = 63;
}
pcs = []

function addBlock (id, func, def) {
    kmap = new Map()
    for (i in pcs ) {
        for (const [tn, tv] of Object.entries(func(i))) {
            kmap.set(tn, tv)
        }
    }
    keys = []
    for (var k of kmap.keys()) {
        keys.push(k)
    }
    keys.sort()
    keys.forEach(function (k) {
        s=''
        for (i in pcs) {
            v = func(i)[k]
            if (v) {
                s+='<td  bot="!'+(id=='weapons'?'a':'c')+' '+k.replace(' ','_')+' <@!'+pcs[i]['memberId']+'>">'+v+'</td>'
            } else {
                s+='<td >'+def+'</td>'
            }
        }
        $('#'+id).append('<tr added="'+id+'"><th  bot="!team '+k.replace(' ','_')+'">'+k+'</th>'+s+'</tr>')
    })

}


function redraw() {
    for (i in pcs ) {
        console.log(i+':'+pcs[i]['shortName'])
        $('.name').append('<th added="name">'+pcs[i]['shortName']+'</th>')
        $('#siz').append('<td added="siz">'+pcs[i]['stats']['siz']+'</td>')
        $('#dex').append('<td added="dex">'+pcs[i]['stats']['dex']+'</td>')
        $('#con').append('<td added="con">'+pcs[i]['stats']['con']+'</td>')
        $('#str').append('<td added="str">'+pcs[i]['stats']['str']+'</td>')
        $('#app').append('<td added="app">'+pcs[i]['stats']['app']+'</td>')
        
        $('#dam').append('<td added="dam">'+Math.round((pcs[i]['stats']['str']*1+pcs[i]['stats']['siz']*1)/6)+'</td>')
        $('#hr').append('<td added="hr">'+Math.round((pcs[i]['stats']['str']*1+pcs[i]['stats']['con']*1)/10)+'</td>')
        $('#mr').append('<td added="mr">'+Math.round((pcs[i]['stats']['dex']*1+pcs[i]['stats']['siz']*1)/10)+'</td>')
        mhp = Math.round((pcs[i]['stats']['con']*1+pcs[i]['stats']['siz']*1));
        $('#mhp').append('<td added="hp">'+mhp+'</td>')
        ahp = mhp;
        s='Changes: '
        if (pcs[i]['health'] && pcs[i]['health']['changes']) {
            for(ii in  pcs[i]['health']['changes']) {
                console.log(i)
                if (ii>0) {
                  s+=', '
                }
                s+=pcs[i]['health']['changes'][ii];
                ahp += pcs[i]['health']['changes'][ii];
            }
        }
        if (ahp==mhp) {
            $('#ahp').append('<td added="ahp"><span style="color:green">'+ahp+'</span></td>')
            $('#chi').append('<td added="chi"><span style="color:green">-</span></td>')
        } else  {
            $('#ahp').append('<td added="ahp" title="'+s+'"><span style="color:red">'+ahp+'</span></td>')
            if (pcs[i]['health']['chirurgery']) {
                $('#chi').append('<td added="chi"><span style="color:red">Yes</span></td>')
            } else {
                $('#chi').append('<td added="chi"><span style="color:green">No</span></td>')
            }
        }
        $('#unc').append('<td added="unc">'+Math.round((pcs[i]['stats']['con']*1+pcs[i]['stats']['siz']*1)/4)+'</td>')
        $('#mw').append('<td added="mw">'+pcs[i]['stats']['con']+'</td>')
        $('#kno').append('<td added="kno">'+pcs[i]['stats']['siz']+'</td>')
             
    }
    for (t in traits) {

        tn = traits[t][0].substr(0,3).toLowerCase();
        s0 =  ''
        s1 =  ''
        for (i in pcs ) {
            s0+='<td bot="!c '+traits[t][0].replace(' ','_')+' <@!'+pcs[i]['memberId']+'>">'+pcs[i]['traits'][tn]+'</td>'
            s1+='<td bot="!c '+traits[t][1].replace(' ','_')+' <@!'+pcs[i]['memberId']+'>">'+(20-pcs[i]['traits'][tn]*1)+'</td>'
        }
        $('#traits').append('<tr added="trait_'+tn+'0"><th bot="!team '+traits[t][0].replace(' ','_')+'">'+traits[t][0]+'</th>'+s0+'</tr>')
        $('#traits').append('<tr added="trait_'+tn+'1"><th bot="!team '+traits[t][1].replace(' ','_')+'">'+traits[t][1]+'</th>'+s1+'</tr>')
    }
    addBlock('combat', function(i) { return pcs[i]['skills']['Combat']},'--')
    addBlock('weapons', function(i) { return pcs[i]['skills']['Weapons']},'--')
    addBlock('other', function(i) { return pcs[i]['skills']['Other']},'--')
    addBlock('passions', function(i) { return pcs[i]['passions']},'--')
    $('[bot]').click(function(){
        $.post('https://discord.com/api/webhooks/822974917816483870/J5FB3eGrDP1xJ9FYeZaVIISz8YEHEl2b7rLZN8i0sc1OE4NQ-DVh41e_DUH3Saw7LabU',
         {username: 'WebHook', content:$(this).attr('bot')})
    })
    $('[title]').tooltip()
}

  $( function() {
      $.get( surl+"/players",function( list ) {
        pcs = list
        redraw()
      });
//
  });
