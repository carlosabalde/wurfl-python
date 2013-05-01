<?php
/**
 * test case
 */

require_once dirname(__FILE__).'/../classautoloader.php';

class WURFL_Issues_IssuesTest extends PHPUnit_Framework_TestCase {

    const RESOURCES_DIR = "../../../resources";

    protected static $wurflManager;

    protected static $persistenceProvider;

    public static function setUpBeforeClass() {
        $resourcesDir = dirname(__FILE__) . DIRECTORY_SEPARATOR . self::RESOURCES_DIR;
        $config = new WURFL_Configuration_InMemoryConfig ();
        $config->wurflFile($resourcesDir . "/wurfl-2.0.27.zip")
                ->wurflPatch($resourcesDir . "/web_browsers_patch.xml")
                ->wurflPatch($resourcesDir . "/issues/nokia-patch.xml")
                ->wurflPatch($resourcesDir . "/issues/issue-177-patch.xml");

        self::$persistenceProvider = new WURFL_Storage_Memcache();
        self::$persistenceProvider->clear();
        $wurflManagerFactory = new WURFL_WURFLManagerFactory ($config, self::$persistenceProvider);
        self::$wurflManager = $wurflManagerFactory->create();
    }

    public static function tearDownAfterClass() {
        //echo "Tear Down\n";
        // FIXME: tear down is happening before tests are finished 
        //self::$persistenceProvider->clear();
    }


    /**
     * test
     * @dataProvider issuesProvider
     */
    public function testIssues($userAgent, $deviceId) {
        $deviceFound = self::$wurflManager->getDeviceForUserAgent($userAgent);
        $this->assertEquals($deviceId, $deviceFound->id, $userAgent);
    }

    const ISSUES_FILE = "issues.txt";

    public static function issuesProvider() {
        $fullTestFilePath = dirname(__FILE__) . DIRECTORY_SEPARATOR . self::ISSUES_FILE;
        $lines = file($fullTestFilePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        $map = array();
        foreach ($lines as $line) {
            if (strpos($line, "#") !== 0) {
                $map [] = explode("=", $line);
            }
        }
        return $map;
    }

    public function testIssue154() {
        $userAgent = "Nokia8800e-1/2.0 (10.00) Profile/MIDP-2.1 Configuration/CLDC-1.1";
        $deviceFound = self::$wurflManager->getDeviceForUserAgent($userAgent);
        $this->assertEquals("nokia_8800e_ver1", $deviceFound->id);
    }

    public function testIssueHeroIdentifiedAsDesireUfterUpdate() {
        $userAgent = "Mozilla/5.0 (Linux; U; Android 2.1-update1; de-de; HTC Hero Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17";
        $deviceFound = self::$wurflManager->getDeviceForUserAgent($userAgent);
        $this->assertEquals("htc_hero_ver1_subandroid21saf4", $deviceFound->id);

    }

    public function testIssue54ModelNameAndBrandNameNotReturnedByWURFL() {
        $userAgent = "NexianNX-G922/MTK Release/7.15.2009 Browser/MAUI Profile/MIDP-2.0 Configuration/CLDC-1.0";
        $deviceFound = self::$wurflManager->getDeviceForUserAgent($userAgent);
        $this->assertEquals("nexian_nx_g922_ver1", $deviceFound->id);
        $this->assertEquals("Nexian", $deviceFound->getCapability("brand_name"));
        $this->assertEquals("NX G922", $deviceFound->getCapability("model_name"));
    }

    /**
     * @test
     * @dataProvider issue17UnrecognizedDevices
     */
    public function testIssue17UnrecognizedDeviceSamsung($userAgent, $deviceId) {
        $deviceFound = self::$wurflManager->getDeviceForUserAgent($userAgent);
        $this->assertEquals($deviceId, $deviceFound->id);

    }

    /**
     * Nokia3220 UP.Browser/7.0.2.3.119 (GUI) MMP/2.0 Push/PO are old phones
     * so it ok to return the opwv if the user-agent is not present in wurfl.
     */
    public static function issue17UnrecognizedDevices() {
        return array(
            array("SAMSUNG-SGH-J700i/J700IXAIA2 Profile/MIDP-2.0 Configuration/CLDC-1.1 UP.Browser/6.2.3.3.c.1.101 (GUI) MMP/2.0", "samsung_sgh_j700i_ver1"),
            array("Nokia3220 UP.Browser/7.0.2.3.119 (GUI) MMP/2.0 Push/PO", "nokia_3220_ver1"));
    }

    public function testIssue117() {
        $device = self::$wurflManager->getDevice("apple_iphone_ver4_1");
        $this->assertEquals("Apple", $device->getCapability("brand_name"));
        $this->assertEquals("true", $device->getCapability("transparent_png_alpha"));
    }

    public function testBlackBerryIdentifiedAsGeneric() {
        $userAgent = "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.135 Mobile Safari/534.1+";
        $deviceFound = self::$wurflManager->getDeviceForUserAgent($userAgent);
        $this->assertEquals("blackberry9800_ver1", $deviceFound->id);
    }

    public function testIphoneIdentifiedWithWrongVersion() {
        $userAgent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_1 like Mac OS X; fr-fr) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8B5097d Safari/6531.22.7";
        $deviceFound = self::$wurflManager->getDeviceForUserAgent($userAgent);
        $this->assertEquals("apple_iphone_ver4_1", $deviceFound->id);

    }

}

