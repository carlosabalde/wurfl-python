<?php
/**
 * test case
 */

require_once dirname(__FILE__).'/../classautoloader.php';

class WURFL_Xml_DeviceIteratorTest extends PHPUnit_Framework_TestCase {
	
	const RESOURCES_DIR = "../../../resources/";
	const WURFL_FILE = "../../../resources/wurfl_base.xml";
	
	/**
	 * @expectedException InvalidArgumentException
	 */
	public function testShouldLaunchExceptionForInvalidInputFile() {
		$wurflFile = "";
		new WURFL_Xml_DeviceIterator ( $wurflFile );
	
	}
	
	public function testShouldReadTheSpecificAttribute() {
		$wurflFile = dirname ( __FILE__ ) . DIRECTORY_SEPARATOR . self::RESOURCES_DIR . "wurfl-specific-attribute.xml";
		
		$deviceIterator = new WURFL_Xml_DeviceIterator ( $wurflFile );
		$devices = $this->toList($deviceIterator);
		
		$this->assertEquals("foo", $devices[0]->id);
		$this->assertTrue($devices[0]->specific);
		
		$this->assertFalse($devices[1]->specific);
	}
	
	private function toList($deviceIterator) {
		$deviceList = array();
		foreach ($deviceIterator as $device) {
			$deviceList[] = $device;
		}
		return $deviceList;
	}
	
	public function testShouldLoadAllCapabilties() {
		$wurflFile = dirname ( __FILE__ ) . DIRECTORY_SEPARATOR . self::WURFL_FILE;
		
		$deviceIterator = new WURFL_Xml_DeviceIterator ( $wurflFile );
		foreach ( $deviceIterator as $device ) {
			$capsByGroupsId = $device->getGroupIdCapabilitiesMap ();
			$this->assertTrue ( count ( $capsByGroupsId ) > 2 );
		}
	}
	
	public function testShouldLoadAllCapabilitiesInAGroup() {
		$capabilities = array ("product_info" => "" );
		$wurflFile = dirname ( __FILE__ ) . DIRECTORY_SEPARATOR . self::WURFL_FILE;
		$deviceIterator = new WURFL_Xml_DeviceIterator ( $wurflFile, $capabilities );

		$capabilitiesSelected = array ("brand_name", "model_name", "unique", "ununiqueness_handler", "is_wireless_device", "device_claims_web_support", "has_pointing_device", "has_qwerty_keyboard", "can_skip_aligned_link_row", "uaprof", "uaprof2", "uaprof3", "device_os" );		
		foreach ( $deviceIterator as $device ) {
			if(strcmp($device->id, "generic") === 0) {
				$this->assertEquals ( $capabilitiesSelected, array_keys ( $device->getCapabilities () ) );				
			}
		}
	}
	
	public function testShouldLoadOnlyTheSpecifiedCapbilties() {
		$capabilities = array ("product_info" => "is_wireless_device, device_claims_web_support" );
		$wurflFile = dirname ( __FILE__ ) . DIRECTORY_SEPARATOR . self::WURFL_FILE;
		$deviceIterator = new WURFL_Xml_DeviceIterator ( $wurflFile, $capabilities );
		
		foreach ( $deviceIterator as $device ) {
			$this->assertEquals ( array ("is_wireless_device", "device_claims_web_support" ), array_keys ( $device->getCapabilities () ) );
		}
	
	}
	
	private function process($device) {
		$this->assertNotNull ( $device );
	}

}

