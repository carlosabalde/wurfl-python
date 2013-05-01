<?php

/**
 * @copyright (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
 * @license GPL, see LICENSE.txt for more details.
 */

// Check input arguments.
if ($argc < 2) {
    error_log("Usage: ' . __FILE__ . ' <user agent string>\n", 0);
    exit(1);
}
$ua = $argv[1];

// Setup WURLF PHP.
require_once dirname(__FILE__) .'/../wurfl-php/WURFL/Application.php';
$wurflConfig = new WURFL_Configuration_InMemoryConfig();
$wurflConfig->wurflFile(dirname(__FILE__) . '/../wurfl-db/wurfl.xml');
$wurflConfig->matchMode('accuracy');
$wurflManagerFactory = new WURFL_WURFLManagerFactory($wurflConfig);
$wurflManager = $wurflManagerFactory->create();

// Dump Python module & match UAs.
$device = $wurflManager->getDeviceForUserAgent($ua);
echo $device->id;
