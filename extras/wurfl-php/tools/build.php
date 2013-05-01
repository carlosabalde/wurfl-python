<?php


define("WURFL_DIR", dirname(__FILE__) . '/../WURFL/');
define("RESOURCES_DIR", WURFL_DIR . "../examples/resources/");

require_once WURFL_DIR . 'Application.php';

$persistenceDir = RESOURCES_DIR . "storage/persistence";
$wurflConfig = new WURFL_Configuration_InMemoryConfig ();
$wurflConfig
        ->wurflFile(RESOURCES_DIR . "wurfl.zip")
        ->persistence("file", array(
    WURFL_Configuration_Config::DIR => $persistenceDir));






function buildPersistenceWith($wurflConfig) {
    $persistenceStorage = WURFL_Storage_Factory::create($wurflConfig->persistence);
    $context = new WURFL_Context ($persistenceStorage);
    $userAgentHandlerChain = WURFL_UserAgentHandlerChainFactory::createFrom($context);
        
    $devicePatcher = new WURFL_Xml_DevicePatcher ();
    $deviceRepositoryBuilder = new WURFL_DeviceRepositoryBuilder ($persistenceStorage, $userAgentHandlerChain, $devicePatcher);

    return $deviceRepositoryBuilder->build($wurflConfig->wurflFile, $wurflConfig->wurflPatches);
}



buildPersistenceWith($wurflConfig);