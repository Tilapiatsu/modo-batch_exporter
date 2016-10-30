#perl
# MeshOut.pl
#   Copyright (c) 2001-2016, The Foundry Group LLC
#   All Rights Reserved. Patents granted and pending.
# Duplicate Fusion Item, Convert to Mesh Item, Delete children of new Mesh Item
# Optionally converts original to mesh to avoid 'un-ready' state of duplicate

# Fusion Plugin Kit for MODO
# © Braid Art Labs 2015

$sMode = $ARGV[0];
$aMode = 0;

my $newSDF = "";
my $dupSDF = "";
my $noHier = 0;
my $origDup = 0;
my $origName = "";
my $newName = "";
my @iKids = ();
my $oPartName = "";
my $sdfTag = "";

if($sMode != 1)
	{$sMode = lxq( "user.value sdf.outCon ?" );}

# Check for one Fusion Item Selected
my @selectedSDF = lxq( "query sceneservice selection ? sdf.item" );
my $selSDFCount = @selectedSDF;


if($selSDFCount > 1)
	{
	$gBoto_diatitle = "Fusion - Create Mesh Item";
	$gBoto_dMsg = "Multiple Fusion Items Selected - Please Select just one.";
	lx( "dialog.setup info");
	lx( "dialog.title {$gBoto_diatitle}" );
	lx( "dialog.msg {$gBoto_dMsg}");
	lx( "dialog.open");
	lx( "dialog.result ok");
	$gBoto_diaResult = lxq( "dialog.result ?");
	return;
	}
elsif($selSDFCount == 0)
	{
	$gBoto_diatitle = "Fusion - Create Mesh Item";
	$gBoto_dMsg = "Fusion Item selection required.";
	lx( "dialog.setup info");
	lx( "dialog.title {$gBoto_diatitle}" );
	lx( "dialog.msg {$gBoto_dMsg}");
	lx( "dialog.open");
	lx( "dialog.result ok");
	$gBoto_diaResult = lxq( "dialog.result ?");
	return;
	}

$newSDF = lxq( "query sceneservice selection ? sdf.item" );
$mMode = lxq( "channel.value ? channel:{${newSDF}:OutputMeshMode}" );
$stripRows = lxq( "channel.value ? channel:{${newSDF}:StripRows}" );
$xRows = lxq( "channel.value ? channel:{${newSDF}:StripExtraRow}" );
$uvOn = lxq( "channel.value ? channel:{${newSDF}:FusionUVon}" );
$sdfTag = lxq( "item.tag string sDfi ?" );

vlxout( 2, "OutputMode:${mMode} Xtra:${xRows} UV:${uvOn}");

if($mMode ne "outModeFinal" && $mMode ne "outModeFinalParts" && $aMode == 1) #v102 Alert if not Final Airtight
	{	
	$gBoto_diatitle = "Fusion Output Mesh Mode";
	$gBoto_dMsg = "Current Mesh Mode is not Airtight Final\n
	Airtight Final is recommended for best quality and Airtight Final-Parts required for Part Tags.\n
	Convert anyway?";
	lx( "dialog.setup yesNo");
	lx( "dialog.title {$gBoto_diatitle}" );
	lx( "dialog.msg {$gBoto_dMsg}");
	lx( "dialog.open");
	
	$gBoto_diaResult = lxq( "dialog.result ?");
	if($gBoto_diaResult ne "ok")										
		{return;}
	}
	
my $oMaterial = lxq( "user.value sdf.outMat ?" );	
my $mMode = lxq( "channel.value ? channel:{${newSDF}:OutputMeshMode}" );

if($mMode eq "outModeFinalParts" && ! $oMaterial) #v105 Alert if Final Airtight w/Parts and Materials Off
	{	
	lx( "channel.value outModeFinal channel:{${newSDF}:OutputMeshMode}" );
	$mMode = lxq( "channel.value ? channel:{${newSDF}:OutputMeshMode}" );
	vlxout( 2, "ModeReset Mode $mMode");

	$gBoto_diatitle = "Material Groups Off";
	$gBoto_dMsg = "Fusion Mesh Mode must reset Airtight Final if you do Not want Material Groups.\n
	Reset to Airtight Final and proceed?.\n";
	lx( "dialog.setup okCancel");
	lx( "dialog.title {$gBoto_diatitle}" );
	lx( "dialog.msg {$gBoto_dMsg}");
	lx( "dialog.open");
	
	$gBoto_diaResult = lxq( "dialog.result ?");
	if($gBoto_diaResult ne "ok")										
		{
		lx( "channel.value outModeFinalParts channel:{${newSDF}:OutputMeshMode}" );
		return;
		}

	lx( "channel.value outModeFinal channel:{${newSDF}:OutputMeshMode}" );
	$mMode = lxq( "channel.value ? channel:{${newSDF}:OutputMeshMode}" );
	vlxout( 2, "ModeReset Mode $mMode");
		
	}

# Detection of Schematic Fusion
my $firstNode = "";
@iKids = lxq( "query sceneservice item.children ? ${newSDF}" );
my $kCount = @iKids;
my $fusionLink = "";

if($kCount == 0)
	{$noHier = 1;}
else
	{
	$firstNode = @iKids[0];
	if($firstNode eq "")
		{$noHier = 1;}
	else
		{
		$firstNodeType = lxq( "query sceneservice item.type ? ${firstNode}" );
		if($firstNodeType ne "locator")
			{$noHier = 1;}
		if($firstNodeType eq "groupLocator")
			{$noHier = 1;}
		}
	}
if($noHier == 1)
	{
	lx("script.implicit GraphRevLinks.py");
	$fusionLink = lxq("user.value sdf.schKid ?");
	vlxout( 1, "FusionLink - ${fusionLink}");
	}

# Mode 1 is simple Conversion - Mode 0 is Dup & Convert
# Dup & Convert has option to convert original ($convertOrig)
my $convertOrig = lxq( "user.value sdf.outDup ?" );	
if($sMode == 1)
	{$convertOrig = 1;}
	
	vlxout( 2, "sMode ${sMode} - convertOrig ${convertOrig}");
	

lx( "channel.value 0 channel:{${newSDF}:visible}" );

if($noHier && $convertOrig)
	{
	@noxy = nodeXY($origSDF);
	vlxout( 2, "NODEXY - @noxy");
	@noxyx = nodeXY($dupSDF);
	lx( "schematic.nodePosition  x:@noxy[0] y:@noxy[1] mode:abs drag:false");
	}
	
# Remove any errant FusionItem Transforms
lx( "!select.channel {${newSDF}:tLock} add" );
lx( "!select.channel {${newSDF}:sLock} add" );
$isChanLock = lxok;
vlxout( 2, "isChanLOCK - ${isChanLock}");
lx( "!channel.delete" );
lx( "select.drop channel" );


if($isChanLock)
	{
	$rotChan = lxq( "query sceneservice item.xfrmRot ? ${newSDF}" );
	$isChan = lxok;
	vlxout( 2, "isChanROT - ${isChan}  ${rotChan}");
	if($isChan && $rotChan ne "")
		{
		lx( "channel.value 0 channel:{${rotChan}:rot.X}" );
		lx( "channel.value 0 channel:{${rotChan}:rot.Y}" );
		lx( "channel.value 0 channel:{${rotChan}:rot.Z}" );
		}
	$posChan = lxq( "query sceneservice item.xfrmPos ? ${newSDF}" );
	$isChan = lxok;
	if($isChan && $posChan ne "")
		{
		lx( "channel.value 0 channel:{${posChan}:pos.X}" );
		lx( "channel.value 0 channel:{${posChan}:pos.Y}" );
		lx( "channel.value 0 channel:{${posChan}:pos.Z}" );
		}
	$sclChan = lxq( "query sceneservice item.xfrmScl ? ${newSDF}" );
	$isChan = lxok;
	if($isChan && $sclChan ne "")
		{
		lx( "channel.value 1 channel:{${sclChan}:scl.X}" );
		lx( "channel.value 1 channel:{${sclChan}:scl.Y}" );
		lx( "channel.value 1 channel:{${sclChan}:scl.Z}" );
		}
	}
	
# Make new Mesh Item Selectable
lx( "select.drop item" );
lx( "select.subItem ${newSDF} set" );
lx( "channel.value on channel:{${newSDF}:select}" );

lx( "!item.tagAdd sDfi" );
if ($sdfTag == '')
	{$sdfTag = "0";}
lx( "item.tag string sDfi ${sdfTag}" );				

$sdfName = lxq( "query sceneservice item.name ? ${newSDF}" );

# V105 Changes for better dialog workflow — also required intervening dialog below if(!$origDup)

# Set user value to altered name - then prompt user for name
# lx( "user.value sdf.meshOutName {${newName}}" );

$newName = lxq( "user.value sdf.meshOutName ?" );


# Convert, Rename, Delete Fusion Hierarchy
lx( "item.setType mesh locator" );
$newMesh = lxq( "query sceneservice selection ? mesh" );
lx( "item.name {${newName}}" );
lx( "select.itemHierarchy" );
lx( "select.subItem ${newMesh} remove" );
lx( "!item.delete" );


# If converting original, change duplicate name to original name
if($origDup)
	{lx( "item.name name:{${origName}} item:${dupSDF}" );}

if($noHier == 1 && $fusionLink ne "_" && $fusionLink ne "")
	{
	if($convertOrig && $sMode == 0)
		{
		@fusionLinks = split(/ /, $fusionLink);
		lx( "!channel.link add {@fusionLinks[0]:@fusionLinks[1]} {${dupSDF}:FusionTreeIn}" );
		lx( "select.channel {${dupSDF}:FusionTreeIn} set" );
		lx( "!schematic.addChannel" );
		lx( "select.drop channel" );
		}
	lx( "!schematic.remItem ${newMesh}" );
	}


	vlxout( 2, "origDup ${origDup} - newSDF ${newSDF} - origSDF ${origSDF} - dupSDF ${dupSDF} - sMode ${sMode} - convertOrig ${convertOrig}");

if($origDup && $sMode == 0)
	{lx( "channel.value allOff channel:{${dupSDF}:visible}" );}
elsif($sMode == 0)
	{lx( "channel.value allOff channel:{${origSDF}:visible}" );}

	
lx( "select.drop item" );
lx( "select.subItem ${newMesh} set" );
lx( "!select.channel {${newMesh}:tLock} add" );
lx( "!select.channel {${newMesh}:sLock} add" );
lx( "!channel.delete" );
lx( "select.drop item" );
lx( "select.subItem ${newMesh} set" );

@opN = lxq( "query layerservice parts ? fg");
foreach $opi (@opN)
	{
	$pName = lxq( "query layerservice part.name ? ${opi}" );
	$oPartName = $oPartName . " " . $pName;
	}
vlxout( 2, "OriginalParts - @opN");
vlxout( 2, "oPartName - ${oPartName}");

$omID = lxq( "query layerservice layer.id ? current" );
vlxout( 2, "OutLayerID ${omID}");

# v102 no longer needed
# lx( "!mesh.cleanup false false false false false true false false false true" );
if($mMode eq "outModeFinalParts")
	{moreParts($stripRows, $newMesh, $omID, $sdfName);}


sub moreParts	# material/parts to center of Strip
	{
	my $sRows = $_[0];
	my $oMesh = $_[1];
	my $mID = $_[2];
	my $fName = $_[3];
	
	$fName = $fName . " Strips";
	
	# Weld Verts
	my $oMerge = lxq( "user.value sdf.outMerge ?" );	
	if($oMerge)										
		{
		lx( "select.drop vertex" );
		lx( "select.typeFrom vertex;ptag;item;pivot;center;edge;polygon true" );
		lx( "select.all" );
		lx( "!vert.merge auto false morph:false disco:true" );	
		lx( "select.drop vertex" );
		}

	lx( "select.drop item" );
	lx( "select.subItem ${oMesh} set" );

	my $oMaterial = lxq( "user.value sdf.outMat ?" );	
	# V105 change -- was if($oMaterial) -- probably unneeded
	if($oMaterial > 0)										
		{
		$pN = lxq( "query layerservice part.N ? fg" );
		vlxout( 2, "LayerIx - ${lix} PartCount - ${pN}");
		@pN = lxq( "query layerservice parts ? fg");
		vlxout( 2, "LayerParts @pN");
		vlxout( 2, "LayerPartCount ${pN}");
		
# removed for 10.1v1 crash bug
#		lxmonInit($pN);
		foreach $pi (@pN)
			{
			if($pi >= 0)
				{
				lx( "select.drop polygon" );

				$pName = lxq( "query layerservice part.name ? ${pi}" );
				vlxout( 2, "Parts - Name:${pName} Layer:${pLayer} LayerIndex:${lix}");

				lx( "select.type polygon" );
				lx( "select.all" );
				@selPolys = lxq( "query layerservice polys ? selected" );
				$selPoAll = @selPolys;
				
				lx( "select.polygon remove part face {${pName}}" );
				@selPolys = lxq( "query layerservice polys ? selected" );
				$selPoRem = @selPolys;

				vlxout( 2, "AnyPart - Name:${pName} All:${selPoAll} Rem:${selPoRem}");
				$validPart = 0;
				if($selPoAll > $selPoRem && $selPoRem > 0)
					{
					vlxout( 2, "ValidPart - Name:${pName} All:${selPoAll} Rem:${selPoRem}");
					$validPart = 1;
					}
				lx( "select.drop polygon" );




				$outPart = 1;
				if(index($pName, $fName) > -1)
					{$outPart = 0;}
			
				vlxout( 2, "outPart - ${outPart} ${pName}");
				if($outPart && $validPart)
					{
					lx( "select.typeFrom polygon;edge;vertex;item;pivot;center;ptag false" );
					lx( "select.type polygon" );
					lx( "select.polygon add part face {${pName}}" );
					
					@pnamep = split(/ /, $pName);
					$pnL = @pnamep;
					$tPname = @pnamep[0];
					for($sri = 1; $sri < $pnL - 1; $sri++)
						{$tPname = $tPname . " " . @pnamep[$sri] }
					
					for($sri = 0; $sri < $sRows; $sri++)
						{lx( "select.expand" );}
						
					$newPartName = $pName . " M";
					$newPartName = $tPname;
					lx( "poly.setMaterial name:{${newPartName}}" );
					vlxout( 2, "NewMaterial - ${newPartName}");
					}
				}
# removed for 10.1v1 crash bug
#			if(!lxmonStep())
#				{
#				last;
#				}
			}
		}
	lx( "select.drop polygon" );
	lx( "select.drop item" );
	return;
	}

sub nodeXY	# get position of item's corresponding node for schematic D&D
	{
	# $nodeItem is either mesh, meshInst or Fusion channel modifier
	my $nodeItem = $_[0];
	my @nxy = (-20,0);

	# scan all scene nodes - selecting each individually
	# selecting a node also selects its corresponding item
	# matching that selected item with the argument[0] $nodeItem gives us our $nodeItem's node
	# ...and then it's location
	$nCount = lxq( "query sceneservice schmNode.n ?" );
	for ( $i = 0; $i < $nCount; $i++)
		{
		lx( "select.drop item" );
		lx( "select.drop schmNode" );
		$snon = lxq( "query sceneservice schmNode.id ? ${i}" );
		lx( "select.node ${snon} set ${snon}" );
		$selectedS = lxq( "query sceneservice selection ? all" );
		if($selectedS eq $nodeItem)
			{
			@nxy[0] = lxq( "schematic.nodePosition x:?");
			@nxy[1] = lxq( "schematic.nodePosition y:?");
			last;
			}
		}
	return @nxy;
	}

sub vlxout	# for debugging
	{
	$verbose = -1;
	$vLevel = $_[0];
	$dString = $_[1];
	if($vLevel <= $verbose)
		{
		lxout($dString);
		}
	return;
	}



